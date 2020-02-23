# takes a graph in tuple form, and
# returns two hash maps of the graph, M_in and M_out;
# M_out = {subj: {r1 : (obj1, obj2, ...), ...}, ...}
# M_in  = {obj: {r1: (subj1, subj2, ...), ...}, ...}
def generate_maps(graph):
    M_out = dict()
    M_in = dict()
    for triple in graph:
        subject = triple[0]
        predicate = triple[1]
        object = triple[2]

        node_dict1 = M_out.setdefault(subject, dict())
        rel_set1 = node_dict1.setdefault(predicate, set())
        rel_set1.add(object)

        node_dict2 = M_in.setdefault(object, dict())
        rel_set2 = node_dict2.setdefault(predicate, set())
        rel_set2.add(subject)
    return M_out, M_in


# takes a path to ttl file, and
# returns a set of triples (in tuple form)
def parse_triples(fileName):
    triples = set()
    with open(fileName, 'r') as file:
        for line in file:
            if line.endswith("\n"):
                line = line[:-1]
            if line.endswith("."):
                line = line[:-1].strip()
            triple = line.split("\t")
            triples.add(tuple(triple))
    return triples


# takes a path to ttl file, and
# returns a set of triples (in tuple form) together with two hash maps of the graph, M_in and M_out;
def process_graph(file_path):
    triples = parse_triples(file_path) # set of tuples
    M_out, M_in  = generate_maps(triples)
    return M_out, M_in, triples