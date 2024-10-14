import networkx as nx
import math
import get_four_basic_tasks
import test_tasks_0
import utils_refactored as utils
import subprocess
import global_definitions

##Types
CPU = 0
SM = 1
CE = 2

class TASK:

    def __init__(self, DAG, period, deadline):
        ##Task properties
        self.DAG = DAG ##Task level 
        self.period = period
        self.deadline = deadline
        ##Computed task features
        self.task_level_all_suspensions = self.recursive_paths()
        self.task_level_suspensions_dict = self.create_suspensions_dict()


        self.task_level_projections = {} ##No predetermined class
        self.generate_projections()

        

    ##This finds paths between any two nodes
    ##use this to update jitter on roots of sm and ce projection dags
    ##!!This function may not be very efficient
    def recursive_paths_between_two_nodes(self, start_node, end_node, path=[]):
        #print("type(path):", type(path), "path:", path, type([start_node]))
        path = path + [start_node]
        if start_node == end_node:
            return [path]
        if start_node not in self.DAG:
            return []
        paths = []
        for node in self.DAG.successors(start_node):
            if node not in path:
                new_paths = self.recursive_paths_between_two_nodes(node, end_node, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    ##Start is the node where search is started, source and destination define an edge
    ##This finds paths between any two nodes of the same type with intermediate different typed nodes
    def recursive_search(self, G, node_start, node_source, node_destination, path, all_paths):
        path.append((node_source, node_destination))
        nodes = dict(G.nodes)
        ##All conditions satisfied, FOUND
        if(nodes[node_destination]["_type"] == nodes[node_start]["_type"] and utils.check_different(G, path)):
            all_paths.append(list(path))
            ##Start with consecutively same types, SKIP
        elif(not utils.check_different(G, path) and len(path) == 2):
            path.pop()
            return
        ##Same types exist but there are other, 
        elif(nodes[node_source]["_type"] == nodes[node_destination]["_type"] and not utils.check_different(G, path)):
            path.pop()
            return
        else:
            new_out_edges = G.out_edges(nbunch = node_destination)
            temp = node_source
            node_source = node_destination
            for edge in new_out_edges:
                node_destination = edge[1]
                self.recursive_search(G, node_start, node_source, node_destination, path, all_paths)

        path.pop()

    def recursive_paths(self):

        nodes = dict(self.DAG.nodes(data=True))
        all_suspensions = []
        for node in nodes:
            out_edges = self.DAG.out_edges(nbunch = node)
            for edge in out_edges:
                path = []
                all_paths = []
                self.recursive_search(self.DAG, node, node, edge[1], path, all_paths)
                all_suspensions.extend(all_paths)


        return all_suspensions


    def create_suspensions_dict(self):

        t = global_definitions.TYPES_ALPHA
        nodes = self.DAG.nodes(data=True)
        suspensions_dict = {}
        enum = 1
        for suspension in self.task_level_all_suspensions: ##Enumerating manually here
            len_suspend = len(suspension)
            source_node = suspension[0][0]
            target_node = suspension[len_suspend - 1][1]

            exist = False
            for key in suspensions_dict:
                if(suspensions_dict[key]['source_node'] == source_node and suspensions_dict[key]['target_node'] == target_node):
                    exist = True
                    suspensions_dict[key]['paths'].append(suspension)

            if(not exist):
                new_key = str(enum)
                suspensions_dict[new_key] = {}
                suspensions_dict[new_key]['source_node'] = source_node
                suspensions_dict[new_key]['target_node'] = target_node
                suspensions_dict[new_key]['type'] = nodes[source_node]["_type"] ##Can further augment this with t up there
                suspensions_dict[new_key]['paths'] = []
                suspensions_dict[new_key]['paths'].append(suspension)
                enum = enum + 1

        return suspensions_dict


    def generate_projections(self):

        types_list = global_definitions.TYPES
        type_names = global_definitions.TYPES_NUMERIC
        
        for _type in global_definitions.TYPES:
            to_generate = nx.DiGraph()
            all_nodes = dict(self.DAG.nodes(data=True))
            all_edges = self.DAG.edges(data=True)
            access_nodes = self.DAG.nodes(data=True)

            ##Add nodes
            for node in all_nodes:
                if(access_nodes[node]["_type"] == _type):
                    node_data = self.DAG.nodes[node]
                    to_generate.add_node(node, **node_data)
            ##Add projection edges
            ##Edges that remains the same, source and target same type
            for edge in all_edges:
                source_node = edge[0]
                target_node = edge[1]
                source_type = all_nodes[source_node]["_type"] 
                target_type = all_nodes[target_node]["_type"]
                if(source_type == _type and target_type == _type):
                    to_generate.add_edge(source_node, target_node, susp_min = 0, susp_max = 0)


            ##Add suspension edges
            for key in self.task_level_suspensions_dict:
                
                suspension = self.task_level_suspensions_dict[key]
                if(suspension['type'] == _type):
                    min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(self.DAG, suspension)
                    to_generate.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)


            if(_type != "0"): ##We are always assuming type 0 is CPU
                ##Therefore, here we add suspension time from CPU root to other projection roots as jitter
                root_nodes = []
                for node in to_generate:
                    if(to_generate.in_degree(node) == 0):
                        root_nodes.append(node)

                task_root = utils.find_roots_in_DAG(self.DAG)
                task_root = task_root[0] ##Currently, only implements single root in task DAG

                for node in root_nodes:
                    paths = self.recursive_paths_between_two_nodes(task_root, node)

                    for path in paths:
                        path.pop() ##Remove the last node at the end of the path which is the root node itself

                    min_extra_jitter = utils.minimum_extra_jitter_from_paths(self.DAG, paths)
                    max_extra_jitter = utils.maximum_extra_jitter_from_paths(self.DAG, paths)


                    to_generate.nodes(data=True)[node]['_amin'] = to_generate.nodes(data=True)[node]['_amin'] + min_extra_jitter
                    to_generate.nodes(data=True)[node]['_amax'] = to_generate.nodes(data=True)[node]['_amax'] + max_extra_jitter

            self.task_level_projections[_type] = to_generate
            print("#################################################")
            print("Type:", _type)
            print("Nodes:")
            for node in to_generate.nodes(data=True):
                print(node)
            for edge in to_generate.edges(data=True):
                print(edge)
            print("#################################################")


                
class TASKSET:

    ##TASKS is a list of TASK objects
    def __init__(self, TASKS):
        
        self.tasks = TASKS
        self.populate_jobs()



    def populate_jobs():

        
        

    
##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    #def __init__(self, DAG, period, deadline):
    DAG1, DAG2, DAG3 = test_tasks_0.return_tasks()
    TASK1 = TASK(DAG1, 350, 350)
    TASK2 = TASK(DAG2, 120, 120)
    TASK3 = TASK(DAG3, 60, 60)
    #TASKSET_ZERO = TASKSET([TASK1, TASK2, TASK3])
    

    

    ##Usage of some functions

    #utils.print_task_level_suspensions_dict(TASK1)
    #utils.visualize_bfs_w_depth(DAG1)
    

