# Sets
set DRAWS;  # Set of historical draws
set COMBINATIONS := 1..2;  # Set for two combinations

# Parameters
param Hovedtall {DRAWS, 1..5};  # Historical main numbers (5 per draw)
param Stjernetall {DRAWS, 1..2};  # Historical star numbers (2 per draw)
param epsilon := 1e-6;  # Small positive number

# Variables
var Next_Hovedtall {COMBINATIONS, 1..5} integer >= 1 <= 50;  # Next main numbers to be drawn
var Next_Stjernetall {COMBINATIONS, 1..2} integer >= 1 <= 12;  # Next star numbers to be drawn

# Binary variables for enforcing uniqueness
var z {COMBINATIONS, 1..5, 1..5} binary;  # For main numbers
var w {COMBINATIONS} binary;  # For star numbers

# Objective function
# Minimize the sum of squared differences from historical draws for both combinations
minimize Total_Error: sum {c in COMBINATIONS, i in DRAWS} (
    sum {j in 1..5} (Next_Hovedtall[c,j] - Hovedtall[i,j])^2 +
    sum {k in 1..2} (Next_Stjernetall[c,k] - Stjernetall[i,k])^2
);

# Constraints

# Ensure main numbers are unique within each combination
subject to Unique_Hovedtall_1 {c in COMBINATIONS, i in 1..4, j in i+1..5}:
    Next_Hovedtall[c,i] - Next_Hovedtall[c,j] <= -1 + 100 * z[c,i,j];

subject to Unique_Hovedtall_2 {c in COMBINATIONS, i in 1..4, j in i+1..5}:
    Next_Hovedtall[c,j] - Next_Hovedtall[c,i] <= -1 + 100 * (1 - z[c,i,j]);

# Ensure star numbers are unique within each combination
subject to Unique_Stjernetall_1 {c in COMBINATIONS}:
    Next_Stjernetall[c,1] - Next_Stjernetall[c,2] <= -1 + 100 * w[c];

subject to Unique_Stjernetall_2 {c in COMBINATIONS}:
    Next_Stjernetall[c,2] - Next_Stjernetall[c,1] <= -1 + 100 * (1 - w[c]);

# Ensure ascending order within each combination
subject to Ascending_Hovedtall {c in COMBINATIONS, i in 1..4}:
    Next_Hovedtall[c,i] + epsilon <= Next_Hovedtall[c,i+1];

subject to Ascending_Stjernetall {c in COMBINATIONS}:
    Next_Stjernetall[c,1] + epsilon <= Next_Stjernetall[c,2];

# Ensure the two combinations are sufficiently different
subject to Different_Combinations:
    sum {j in 1..5} abs(Next_Hovedtall[1,j] - Next_Hovedtall[2,j]) +
    sum {k in 1..2} abs(Next_Stjernetall[1,k] - Next_Stjernetall[2,k]) >= 10;

# Prevent the second combination from being too similar to the first
subject to Diverse_Combinations_Hovedtall {j in 1..5}:
    abs(Next_Hovedtall[1,j] - Next_Hovedtall[2,j]) >= 2;

subject to Diverse_Combinations_Stjernetall {k in 1..2}:
    abs(Next_Stjernetall[1,k] - Next_Stjernetall[2,k]) >= 1;
