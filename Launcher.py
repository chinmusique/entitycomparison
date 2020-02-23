from MSSQApproximation import compute_apprx_MSSQ
from DataProcessing import process_graph
import sys
import random


def generate_random_entity(entities):
    entities = list(entities)
    return random.choice(entities)

if __name__ == "__main__":

    args = sys.argv
    user_input_size = len(args)
    if not (user_input_size == 1 or user_input_size == 3):
        print('invalid number of input arguments')
    else:
        print("...loading the input graph...")
        M_out, M_in, triples = process_graph("./lubm1.ttl")
        print("...input graph of {} triples loaded...".format(len(triples)))

        if len(args) == 1:
            print("...generating a similarity for random input entities:")
            all_entities = {triple[0] for triple in triples}.union({triple[2] for triple in triples})
            entity1 = generate_random_entity(all_entities)
            entity2 = generate_random_entity(all_entities)
        elif len(args) == 3:
            print('...generating similarities for the input entities:')
            entity1 = args[1]; entity2 = args[2]
        print("........", entity1)
        print("........", entity2)
        print()


        for depth in range(1,4,1):
            query = compute_apprx_MSSQ(M_out, M_in, entity1, entity2, depth)
            print("depth {}:\n{}\n".format(depth, query))