# Sets
set DRAWS;  # Set of historical draws
set COMBINATIONS := 1..10;  # Set for ten combinations

# Parameters
param Hovedtall {DRAWS, 1..7};  # Historical main numbers (7 per draw)
param Stjernetall {DRAWS};  # Historical star numbers (1 per draw)
param epsilon := 1e-6;  # Small positive number

# Variables
var Next_Hovedtall {COMBINATIONS, 1..7} integer >= 1 <= 34;  # Next main numbers to be drawn
var Next_Stjernetall {COMBINATIONS} integer >= 1 <= 10;  # Next star numbers to be drawn

# Binary variables for enforcing uniqueness
var z {COMBINATIONS, 1..7, 1..7} binary;  # For main numbers

# Objective function
# Minimize the sum of squared differences from historical draws for all combinations
minimize Total_Error: sum {c in COMBINATIONS, i in DRAWS} (
    sum {j in 1..7} (Next_Hovedtall[c,j] - Hovedtall[i,j])^2 +
    (Next_Stjernetall[c] - Stjernetall[i])^2
);

# Constraints

# Ensure main numbers are unique within each combination
subject to Unique_Hovedtall_1 {c in COMBINATIONS, i in 1..6, j in i+1..7}:
    Next_Hovedtall[c,i] - Next_Hovedtall[c,j] <= -1 + 100 * z[c,i,j];

subject to Unique_Hovedtall_2 {c in COMBINATIONS, i in 1..6, j in i+1..7}:
    Next_Hovedtall[c,j] - Next_Hovedtall[c,i] <= -1 + 100 * (1 - z[c,i,j]);

# Ensure ascending order within each combination
subject to Ascending_Hovedtall {c in COMBINATIONS, i in 1..6}:
    Next_Hovedtall[c,i] + epsilon <= Next_Hovedtall[c,i+1];

# Ensure the combinations are sufficiently different from each other
subject to Different_Combinations {c1 in COMBINATIONS, c2 in COMBINATIONS: c1 < c2}:
    sum {j in 1..7} abs(Next_Hovedtall[c1,j] - Next_Hovedtall[c2,j]) +
    abs(Next_Stjernetall[c1] - Next_Stjernetall[c2]) >= 10;

# Prevent combinations from being too similar to each other
subject to Diverse_Combinations_Hovedtall {c1 in COMBINATIONS, c2 in COMBINATIONS, j in 1..7: c1 < c2}:
    abs(Next_Hovedtall[c1,j] - Next_Hovedtall[c2,j]) >= 2;

subject to Diverse_Combinations_Stjernetall {c1 in COMBINATIONS, c2 in COMBINATIONS: c1 < c2}:
    abs(Next_Stjernetall[c1] - Next_Stjernetall[c2]) >= 1;
