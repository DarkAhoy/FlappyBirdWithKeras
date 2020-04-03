from random import randint, uniform


def crossover(old_weights1, old_weights2):
    """
    need to swap one gene from one network to the other network
    i.e. replace one weight in another network weight
    """

    # random select a gene (weight)
    gene_index = randint(0, len(old_weights1) - 1)

    new_weights1 = old_weights1
    new_weights1[gene_index] = old_weights2[gene_index]
    new_weights2 = old_weights2
    new_weights2[gene_index] = old_weights1[gene_index]

    return [new_weights1, new_weights2]


def mutate(weights, generation):
    """
    iterate throw the weights and change it.
    change about 50% of the weights.
    add a rand between -0.5 and 0.5
    """

    for i in range(len(weights)):
        for j in range(len(weights[i])):
            if uniform(0, 1) > 0.85:
                weights[i][j] += uniform(-0.3, 0.3)
    return weights