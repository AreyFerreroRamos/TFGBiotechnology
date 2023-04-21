import calculation_functions as calculation
import support_functions as support
import show_functions as show
import pandas as pd
import numpy as np
import math
import sys
import os

if len(sys.argv) != 5:
    print("Error: The number of parameters is incorrect. Three files are needed.")
    exit()

if not os.path.isfile(sys.argv[1]):
    print("Error: The first parameter must be a file corresponding to all vertebrate species.")
    exit()

if not os.path.isfile(sys.argv[2]):
    print("Error: The second parameter must be a file corresponding to the metadata of all the samples in the study.")
    exit()

if not os.path.isfile(sys.argv[3]):
    print("Error: The third parameter must be a file with a list of the scientific name that corresponds to the code "
          "that identifies a vertebrate species.")
    exit()

df_vertebrates = pd.read_table(sys.argv[1], delimiter=' ', header=0)
df_metadata = pd.read_table(sys.argv[2], delimiter=';', header=0)

alpha_diversities_individual = {}

matrix_individuals_genus = np.empty((0, 0))
matrix_vertebrates_genus = np.empty((0, 0))

relative_abundances = {}
for bacterial_genus in df_vertebrates.index:
    relative_abundances[bacterial_genus] = 0

num_zeros = num_abundances = num_individuals = num_genus = num_species = 0

for individual in df_vertebrates: 
    row = 1
    for sample in df_metadata[df_metadata.columns[0]]:
        if sample == individual:
            specie = df_metadata.loc[row, df_metadata.columns[2]]
            sample_type = df_metadata.loc[row, df_metadata.columns[4]]
        else:
            row += 1

    num_bacterial_species_per_individual = 0
    for num_bacterial_species_per_genus in df_vertebrates[individual]:
        num_bacterial_species_per_individual += num_bacterial_species_per_genus
        if matrix_individuals_genus.size == 0:
            num_genus += 1

    if matrix_individuals_genus.size == 0:
        matrix_individuals_genus.resize((1, num_genus))
    else:
        matrix_individuals_genus.resize((matrix_individuals_genus.shape[0] + 1, matrix_individuals_genus.shape[1]))

    if specie not in alpha_diversities_individual:
        alpha_diversities_individual[specie] = {'Wild': [], 'Captivity': []}
        if matrix_vertebrates_genus.size == 0:
            matrix_vertebrates_genus.resize((2, num_genus))
        else:
            calculation.normalize_matrix_vertebrates_genus(matrix_vertebrates_genus, num_species, num_individuals_wild,
                                                           num_individuals_captivity)
            num_species += 2
            matrix_vertebrates_genus.resize((matrix_vertebrates_genus.shape[0] + 2, matrix_vertebrates_genus.shape[1]))

    alpha_diversity = pos = column_genus = num_individuals_wild = num_individuals_captivity = 0
    for num_bacterial_species_per_genus in df_vertebrates[individual]:
        relative_abundance = num_bacterial_species_per_genus / num_bacterial_species_per_individual
        if num_bacterial_species_per_genus != 0:
            alpha_diversity += relative_abundance * math.log(relative_abundance)
            relative_abundances[df_vertebrates.index[pos]] += relative_abundance
        else:
            num_zeros += 1
        num_abundances += 1
        pos += 1

        matrix_individuals_genus[num_individuals][column_genus] = relative_abundance
        if sample_type == 'Wild':
            matrix_vertebrates_genus[num_species][column_genus] += relative_abundance
            num_individuals_wild += 1
        else:
            matrix_vertebrates_genus[num_species][column_genus] += relative_abundance
            num_individuals_captivity += 1
        column_genus += 1

    num_individuals += 1
    alpha_diversities_individual[specie][sample_type].append(round(0 - alpha_diversity, 4))

# calculation.normalize_relative_abundances(relative_abundances, num_individuals)
# calculation.t_test(alpha_diversities_individual)

# show.alpha_diversities(alpha_diversities_individual)

# ploter = show.create_ploter(sys.argv[4])

# print("Total zeros: "+str(round(num_zeros / num_abundances * 100, 2))+"%.")
# ploter.histogram(support.to_array(relative_abundances))
# ploter.boxplot(alpha_diversities_individual, sys.argv[3])
