class TreeNode:
    def __init__(self, label1, label2):
        self.label1 = label1
        self.label2 = label2
        self.children = dict()
        self.parent = ""

    def add_child(self, node, rel1_labels, rel2_labels, dir):
        self.children[node] = [[rel1_labels, rel2_labels], dir]  #dir = "in" / "out"


######## pre-processing ########

# takes two hash maps of the graph, M_in and M_out, and the label with entities, and
# returns submaps that only contain in- and out- triples of these entities
def create_submaps(M_out, M_in, label):
    m_out = dict()
    m_in  = dict()
    for node in label:
        if node in M_out:
            M_out_entry = M_out[node]
            for rel, objs in M_out_entry.items():
                obj_set = m_out.setdefault(rel, set())
                obj_set.update(objs)
                if len(obj_set) == 0:
                    m_out.pop(rel)
        if node in M_in:
            M_in_entry = M_in[node]
            for rel, subjs in M_in_entry.items():
                subj_set = m_in.setdefault(rel, set())
                subj_set.update(subjs)
                if len(subj_set) == 0:
                    m_in.pop(rel)
    return m_out, m_in


######## step 1: forward pass ########

# recursively updates the pair tree, given a node that is currently a leaf
def generate_tree(pair_tree_node, M_out, M_in, depth, i):

    child_counter = 0

        # generate submaps for pair tree nodes
    label1, label2 = pair_tree_node.label1, pair_tree_node.label2
    m1_out, m1_in = create_submaps(M_out, M_in, label1)
    m2_out, m2_in = create_submaps(M_out, M_in, label2)


    ################### out-edges #########################################################

        # 1. find triples with the same rel and object: objects turn to constant-type nodes; maps are updated ((s,p,o) is removed)
    m1_out_rels = set(m1_out.keys()); m2_out_rels = set(m2_out.keys())
    common_rels_out = m1_out_rels.intersection(m2_out_rels)

    for rel in common_rels_out:
        common_obj_for_rel = m1_out[rel].intersection(m2_out[rel])
        for obj in common_obj_for_rel:
            new_pair_tree_node = TreeNode({obj}, {obj})
            pair_tree_node.add_child(new_pair_tree_node, {rel}, {rel}, "out"); child_counter += 1

            remove_from_map(m1_out, rel, obj); remove_from_map(m2_out, rel, obj)



        # 2. find remaining common objects (rels are different now)
    objects1 = {obj for rel in m1_out.keys() for obj in m1_out[rel]}
    objects2 = {obj for rel in m2_out.keys() for obj in m2_out[rel]}
    common_objects = objects1.intersection(objects2)

    for obj in common_objects:
        new_pair_tree_node = TreeNode({obj}, {obj})
        rel1_for_obj = {rel for rel in m1_out.keys() if obj in m1_out[rel]}
        rel2_for_obj = {rel for rel in m2_out.keys() if obj in m2_out[rel]}
        pair_tree_node.add_child(new_pair_tree_node, rel1_for_obj, rel2_for_obj, "out"); child_counter += 1



        # 3. recalculcate common relations and group their objects into new nodes (in updated maps, objects are disjoint)
    m1_out_rels = set(m1_out.keys()); m2_out_rels = set(m2_out.keys())
    common_rels_out = m1_out_rels.intersection(m2_out_rels)

    new_nodes = set()

    for rel in common_rels_out:
        obj1_for_rel = m1_out[rel]
        obj2_for_rel = m2_out[rel]

        new_pair_tree_node = TreeNode(obj1_for_rel, obj2_for_rel)
        pair_tree_node.add_child(new_pair_tree_node, {rel}, {rel}, "out"); child_counter += 1
        new_nodes.add(new_pair_tree_node)

    if i < depth:
        for new_node in new_nodes:
            generate_tree(new_node, M_out, M_in, depth, i + 1)



        # 4. find non-common relations and create a node for their objects (at most one node)
    remaining_rels1_out = m1_out_rels.difference(common_rels_out)
    remaining_rels2_out = m2_out_rels.difference(common_rels_out)

    objects1 = {obj for rel in remaining_rels1_out for obj in m1_out[rel]}
    objects2 = {obj for rel in remaining_rels2_out for obj in m2_out[rel]}
    common_objs = objects1.intersection(objects2)
    objects1 = objects1.difference(common_objs)
    objects2 = objects2.difference(common_objs)

    if len(objects1) > 0 and len(objects2) > 0:
        new_pair_tree_node = TreeNode(objects1, objects2)
        pair_tree_node.add_child(new_pair_tree_node, remaining_rels1_out, remaining_rels2_out, "out"); child_counter += 1

        if i < depth:
            generate_tree(new_pair_tree_node, M_out, M_in, depth, i + 1)


    ################### in-edges #########################################################

        # 1. find triples with the same rel and subject: subjects turn to constant-type nodes; maps are updated ((s,p,o) is removed)
    m1_in_rels = set(m1_in.keys()); m2_in_rels = set(m2_in.keys())
    common_rels_in = m1_in_rels.intersection(m2_in_rels)

    for rel in common_rels_in:
        common_subj_for_rel = m1_in[rel].intersection(m2_in[rel])
        for subj in common_subj_for_rel:
            new_pair_tree_node = TreeNode({subj}, {subj})
            pair_tree_node.add_child(new_pair_tree_node, {rel}, {rel}, "in"); child_counter += 1

            remove_from_map(m1_in, rel, subj); remove_from_map(m2_in, rel, subj)



        # 2. find remaining common subjects (rels are different now)
    subjects1 = {subj for rel in m1_in.keys() for subj in m1_in[rel]}
    subjects2 = {subj for rel in m2_in.keys() for subj in m2_in[rel]}
    common_subjects = subjects1.intersection(subjects2)

    for subj in common_subjects:
        new_pair_tree_node = TreeNode({subj}, {subj})
        rel1_for_subj = {rel for rel in m1_in.keys() if subj in m1_in[rel]}
        rel2_for_subj = {rel for rel in m2_in.keys() if subj in m2_in[rel]}
        pair_tree_node.add_child(new_pair_tree_node, rel1_for_subj, rel2_for_subj, "in"); child_counter += 1



        # 3. recalculcate common relations and group their subjects into new nodes (in updated maps, subjects are disjoint)
    m1_in_rels = set(m1_in.keys()); m2_in_rels = set(m2_in.keys())
    common_rels_in = m1_in_rels.intersection(m2_in_rels)

    new_nodes = set()

    for rel in common_rels_in:
        subj1_for_rel = m1_in[rel]
        subj2_for_rel = m2_in[rel]

        new_pair_tree_node = TreeNode(subj1_for_rel, subj2_for_rel)
        pair_tree_node.add_child(new_pair_tree_node, {rel}, {rel}, "in"); child_counter += 1
        new_nodes.add(new_pair_tree_node)

    if i < depth:
        for new_node in new_nodes:
            generate_tree(new_node, M_out, M_in, depth, i + 1)



        # 4. find non-common relations and create a node for their subjects
    remaining_rels1_in = m1_in_rels.difference(common_rels_in)
    remaining_rels2_in = m2_in_rels.difference(common_rels_in)

    subjects1 = {subj for rel in remaining_rels1_in for subj in m1_in[rel]}
    subjects2 = {subj for rel in remaining_rels2_in for subj in m2_in[rel]}
    common_subjs = subjects1.intersection(subjects2)
    subjects1 = subjects1.difference(common_subjs)
    subjects2 = subjects2.difference(common_subjs)

    if len(subjects1) > 0 and len(subjects2) > 0:
        new_pair_tree_node = TreeNode(subjects1, subjects2)
        pair_tree_node.add_child(new_pair_tree_node, remaining_rels1_in, remaining_rels2_in, "in"); child_counter += 1

        if i < depth:
            generate_tree(new_pair_tree_node, M_out, M_in, depth, i + 1)



# takes a root of a tree, traverses the tree, and
# updates tree nodes with parent info
def update_parent_information(parent_node):
    children = parent_node.children.keys()
    for child in children:
        child.parent = parent_node
        update_parent_information(child)

# takes a submap m, a relation (key) and an entity (one of the values), and
# removes the key-value pair from the submap
def remove_from_map(map, r, o):
    r_set = map[r]
    r_set.remove(o)
    if len(r_set) == 0:
        map.pop(r)



######## step 2: backward pass ########

def uncouple_nodes(tree_root, depth, M_out, M_in):
    # step 1 - get pre-leaves
    nodes = get_nodes_at_depth_level(tree_root, depth)

    # step 2 - for each such node get children
    for node in nodes:
        children = node.children
        if len(children) >= 1: # if node is not a leaf

            # step 3 - check triples bw the node and each child node, creating the updated (smaller) copies of the node
            edges = dict() # {child_node : (subs1, subs2)}
            for child, rel_data in children.items():
                direction = rel_data[1]
                if direction == "in":
                    subscript1 = create_subscript(node.label1, child.label1, rel_data[0][0], M_in, M_out)
                    subscript2 = create_subscript(node.label2, child.label2, rel_data[0][1], M_in, M_out)
                else: # "out"
                    subscript1 = create_subscript(node.label1, child.label1, rel_data[0][0], M_out, M_in)
                    subscript2 = create_subscript(node.label2, child.label2, rel_data[0][1], M_out, M_in)
                edges[child] = form_label_pair(subscript1, subscript2)

            # step 4 - group copies by their "subscripts" (labels)
            groups = [[x] for x in range(len(edges))]
            ordered_edges = list(edges)
            for i in range(len(groups)):
                if len(groups[i]) > 0: # the bucket is not already empty
                    subscripts_i = edges[ordered_edges[i]]
                    for j in range(i+1, len(groups)):
                        if len(groups[j]) > 0: # the bucket compared to is not empty
                            subscripts_j = edges[ordered_edges[j]]

                            if compare_subscripts(subscripts_i, subscripts_j): # comparison
                                groups[i].append(j)
                                groups[j].clear()
            groups = [x for x in groups if len(x) > 0]

            # step 5 - update tree
            if len(groups) > 1: # need to split
                parent_node = node.parent
                rel_data = parent_node.children.pop(node)

                for group in groups:
                    labels1 = set(edges[ordered_edges[group[0]]][0])
                    labels2 = set(edges[ordered_edges[group[0]]][1])

                    new_node = TreeNode(labels1, labels2)
                    new_node.parent = parent_node
                    parent_node.children[new_node] = rel_data

                    for child_node_id in group:
                        child_node = ordered_edges[child_node_id]
                        new_node.children[child_node] = node.children[child_node]
                        child_node.parent = new_node


    if depth > 1:
        uncouple_nodes(tree_root, depth - 1, M_out, M_in)


# takes two labels (sets), and
# returns a tuple of frozenset labels
def form_label_pair(label1, label2):
    return (frozenset(label1), frozenset(label2))

# takes the root of the tree and a fixed depth, and
# returns all nodes on that depth level
def get_nodes_at_depth_level(root, depth):
    nodes = [root]
    for n in range(depth):
        children = []
        for node in nodes:
            children.extend(node.children.keys())
        nodes.clear(); nodes = children
    return nodes

# takes a parent node label (for one target node), a child node label (for the same target node),
# relations of the edge bw them, and maps M_out or M_in, and
# returns a subscript of the edge between the parent and child node labels (for that target node)
def create_subscript(label, child_label, edge_rels, Map1, Map2):
    subscript = set()
    if len(label) < len(child_label):
        for e in label:
            if e in Map1:
                for r in edge_rels:
                    if r in Map1[e]:
                        if len(Map1[e][r].intersection(child_label)) > 0:
                            subscript.add(e)
    else:
        for e in child_label:
            for r in edge_rels:
                if r in Map2[e]:
                    subscript = subscript.union(Map2[e][r])
        subscript = subscript.intersection(label)
    return subscript


# takes to pairs of subscripts of the form (frozenset(s_i1), frozenset(s_i2))), and
# returns True if they meet the merge condition, otherwise false
# MERGE condition: (s_i1 == s_j1) and (s_i2 == s_j2)
def compare_subscripts(s_i, s_j):
    if s_i[0] == s_j[0] and s_i[1] == s_j[1]:
        return True
    return False



######## step 3: rewriting ptree into query ########

# takes a tree node, its corresponding term in the query and the query, and
# iteratively updates the query, mapping each non-constant label to a unique variable, and handling inequalities
def translate_tree_into_query(node, term, mssq):
    children = node.children
    if len(children) > 0: # if it is a leaf, then it has already been translated into a term in an atom
        for child_node in children.keys():
            child_label1 = child_node.label1
            child_label2 = child_node.label2

            # create a triple pattern
            child_term = get_term(child_label1, child_label2, True)
            direction = children[child_node][1]
            edge_term = get_term(children[child_node][0][0], children[child_node][0][1], False)
            if direction == "in":
                mssq[0].add((child_term, edge_term, term))
            else:
                mssq[0].add((term, edge_term, child_term))

            # create an arithmetic comparison
            if node_is_numeric(child_label1, child_label2) and not is_constant(child_label1, child_label2):
                all_values = [float(x) for x in child_label1.union(child_label2)]
                mssq[1].add((child_term, '<=', max(all_values)))
                mssq[1].add((child_term, '=>', min(all_values)))

            translate_tree_into_query(child_node, child_term, mssq)


def generate_fresh_variable():
    var_index = translate_tree_into_query.var_index
    variable = "Y_" + str(var_index)
    translate_tree_into_query.var_index = translate_tree_into_query.var_index + 1
    return variable

def generate_fresh_predicate_variable():
    rel_var_index = translate_tree_into_query.rel_var_index
    rel_variable = "R_" + str(rel_var_index)
    translate_tree_into_query.rel_var_index = translate_tree_into_query.rel_var_index + 1
    return rel_variable

# takes a pair of labels for a node, and
# checks whether corresponds to a constant
def is_constant(label1, label2):
    if (len(label1) == len(label2) == 1) and (label1 == label2):
        return True
    return False

# takes the labels of a tree node and a boolean switch, and
# returns a corresponding term in the query (a constant or a new variable)
def get_term(label1, label2, is_node_term):
    if is_constant(label1, label2):
        return next(iter(label1))  # get an element of a set without removing it
    else:
        if is_node_term: # nodes
            fresh_var = generate_fresh_variable()
            return fresh_var
        else: # edges
            fresh_rel_var = generate_fresh_predicate_variable()
            return fresh_rel_var

def node_is_numeric(label1, label2):
    for l in label1.union(label2):
        if not l.replace('.','',1).isdigit():
            return False
    return True

# takes a query of the form [basic graph patter, filter condition], and
# returns a string SPARQL query of the form "Select X? Where P Filter C"
def stringify_query(query):
    return "SELECT ?X \nWHERE {} \nFILTER {}".format(query[0], query[1])


######## main procedure ######################################################

def compute_apprx_MSSQ(m_out, m_in, entity1, entity2, depth):
    label1 = {entity1}
    label2 = {entity2}

    # I. forward pass -- generate a pair tree
    pair_tree_root = TreeNode(label1, label2)
    generate_tree(pair_tree_root, m_out, m_in, depth, 1)
    update_parent_information(pair_tree_root)

    # II. backward pass -- create a similarity tree from pair tree
    uncouple_nodes(pair_tree_root, depth - 1, m_out, m_in)

    # III. translation step -- turn the pair tree into a query
    translate_tree_into_query.var_index = 0
    translate_tree_into_query.rel_var_index = 0

    MSSQ = [set(), set()] # [basic graph patter, filter condition]
    translate_tree_into_query(pair_tree_root, "X", MSSQ)

    return stringify_query(MSSQ)
