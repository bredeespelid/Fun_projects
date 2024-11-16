# Eurojackpot Number Predictor

This project is just for fun!

It implements a mathematical optimization model to predict potential winning numbers for the EuroMillions lottery based on historical draw data.

## Model Description

The model uses integer programming to generate two combinations of EuroMillions numbers based on past draws while ensuring diversity between the combinations.

### Sets

- \( DRAWS \): Set of historical draws
- \( COMBINATIONS := \{1, 2\} \): Set for two combinations

### Parameters

- \( Hovedtall_{d,i} \): Historical main numbers (5 per draw)
- \( Stjernetall_{d,j} \): Historical star numbers (2 per draw)
- \( \epsilon := 10^{-6} \): Small positive number for strict inequalities

### Variables

- \( Next\_Hovedtall_{c,i} \in \mathbb{Z}, 1 \leq Next\_Hovedtall_{c,i} \leq 50 \): Next main numbers to be drawn
- \( Next\_Stjernetall_{c,j} \in \mathbb{Z}, 1 \leq Next\_Stjernetall_{c,j} \leq 12 \): Next star numbers to be drawn
- \( z_{c,i,j} \in \{0,1\} \): Binary variables for enforcing uniqueness of main numbers
- \( w_c \in \{0,1\} \): Binary variables for enforcing uniqueness of star numbers

### Objective Function

Minimize the total error, defined as the sum of squared differences from historical draws for both combinations:

\[
\min \sum_{c \in COMBINATIONS} \sum_{i \in DRAWS} \left( \sum_{j=1}^5 (Next\_Hovedtall_{c,j} - Hovedtall_{i,j})^2 + \sum_{k=1}^2 (Next\_Stjernetall_{c,k} - Stjernetall_{i,k})^2 \right)
\]

### Key Constraints

1. Uniqueness of main numbers within each combination:
   \[
   Next\_Hovedtall_{c,i} - Next\_Hovedtall_{c,j} \leq -1 + 100z_{c,i,j}, \quad \forall c \in COMBINATIONS, i \in \{1,\ldots,4\}, j \in \{i+1,\ldots,5\}
   \]
   \[
   Next\_Hovedtall_{c,j} - Next\_Hovedtall_{c,i} \leq -1 + 100(1-z_{c,i,j}), \quad \forall c \in COMBINATIONS, i \in \{1,\ldots,4\}, j \in \{i+1,\ldots,5\}
   \]

2. Uniqueness of star numbers within each combination:
   \[
   Next\_Stjernetall_{c,1} - Next\_Stjernetall_{c,2} \leq -1 + 100w_c, \quad \forall c \in COMBINATIONS
   \]
   \[
   Next\_Stjernetall_{c,2} - Next\_Stjernetall_{c,1} \leq -1 + 100(1-w_c), \quad \forall c \in COMBINATIONS
   \]

3. Ascending order within each combination:
   \[
   Next\_Hovedtall_{c,i} + \epsilon \leq Next\_Hovedtall_{c,i+1}, \quad \forall c \in COMBINATIONS, i \in \{1,\ldots,4\}
   \]
   \[
   Next\_Stjernetall_{c,1} + \epsilon \leq Next\_Stjernetall_{c,2}, \quad \forall c \in COMBINATIONS
   \]

4. Ensuring the two combinations are sufficiently different:
   \[
   \sum_{j=1}^5 |Next\_Hovedtall_{1,j} - Next\_Hovedtall_{2,j}| + \sum_{k=1}^2 |Next\_Stjernetall_{1,k} - Next\_Stjernetall_{2,k}| \geq 10
   \]

5. Preventing the second combination from being too similar to the first:
   \[
   |Next\_Hovedtall_{1,j} - Next\_Hovedtall_{2,j}| \geq 2, \quad \forall j \in \{1,\ldots,5\}
   \]
   \[
   |Next\_Stjernetall_{1,k} - Next\_Stjernetall_{2,k}| \geq 1, \quad \forall k \in \{1,2\}
   \]

## Usage

To use this model:

1. Prepare your historical draw data in the required format.
2. Solve the optimization problem using an appropriate solver (e.g., CPLEX, Gurobi).
3. The solution will provide two sets of predicted numbers for the next EuroMillions draw.

## Disclaimer

This model is for educational and entertainment purposes only. It does not guarantee winning numbers and should not be used as a basis for gambling decisions.
