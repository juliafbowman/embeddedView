## Embedding Construction

### Preprocessing and Normalization
Some of the processes that were done in order to prepare the dataset for embedding was:

- **Cleaning:** Remove formatting characters like ```%``` or ```,``` from numeric columns.
- **Handling Missing Values:** We filled or dropped ```NaN``` values to ensure vector could be completed.
- **Scaling:** We applied ```MinMaxScaler``` to scale all numeric attributes to a [0,1] range. This ensures that large raw numbers do not dominate features with small decimals like positivity rate.

### Feature Selection

I selected 12 dimensions in order to construct the vector. These features helped to capture the severity, density and the location of the COVID-19 outbreak.

**1. Cases - Cumulative**

**2. Cases - Weekly**

**3. Case Rate - Cumulative**

**4. Tests - Cumulative**

**5. Tests - Weekly**

**6. Test Rate - Cumulative**

**7. Percent Tested Positive - Cumulative**

**8. Percent Tested Positive - Weekly**

**9. Population (Demographic Context)**

**10. Longitude (Spatial Context)**

**11. Latitude (Spatial Context)**

**12. Stratum_Mean_Case_Rate (Aggregated group-based feature)**

### Aggregated Feature

There was a custom feature created called ```Stratum_Mean_Case_Rate```.
- **Method:** The ZIP codes were divided into 4 Population Density Quartiles (Low, Medium, High, Very High).
- **Calculation:** For every week, we created a calculated average Case rate for the specific density group.
- **Rationale:** This allows us to analyze how a specific ZIP Code is performing in relation to other ZIP Codes of similar density.


### Dimensionality Reduction
We had a 12-dimensional vector space get converted to a 2 dimensional vector space.
- **Method:** ```UMAP``` (Uniform Manifold Approximation and Projection)
- **Rationale:** UMAP is a non-linear manifold learning techinique, this non-linearity was something that we were interested in to preserve local neighborhoods and structure. THis made it ideal for identifying clusters of similar behavior.

- **Parameters:**
    
    ``` n_neighbors```: 15 (Balances the local vs global structures)
    
    ``` min_dist```: 0.1 (Controls how tightly the points are placed together)
    
    ```n_components```: 2 (This creates a 2D visualization)

### Iterative Design Process

#### Iteration 1 : Raw Numeric Features & PCA

Initially I selected only a few features like ```Cases - Cumulative``` and ```Tests - Cumulative``` and ```Case Rate - Cumulative``` because those during this whole semester were some of the most important to look at. Then I decided to just add a few more as we started to notice some of the other attributes that could be important to look at patterns, like weekly cases and weekly tests as we can look at things more granularly. initially when only picking three attributes to look at , I had picked ```Principle Component Analysis (PCA)``` because it is good for linear relationships and it was fast. However looking further into it, our data is very large and very complex to the point that trying to convert our data into a 2D mapping would be flattening in a way that does not keep the complexity of the 3D shape in an unfolding manner. Therefore we looked into ```Uniform Manifold Approximation and Projection (UMAP)```. It has a non-linear technique and assumes our data is complex and tries to 'unfold it' in a way that is respective of the original shape. PCA would have resulted to us in a weird blob when looking at images of this technique. UMAP fits better for the type of data that we were working with.

#### Iteration 2: Adding Aggregated Context


After changing to UMAP, high - population ZIP Codes were mixed discriminately with low-population ones. This makes it hard to see any density-based patterns(It is one of the aggregated functions that we took interest in since it hasn't been done before in our assignments) The embedding and visualizations before lacked "group" context. So I engineered the ```Population_Stratum``` feature annd the ```Stratum_Mean_Case_Rate``` in order to provide group context. It divides the Population density into 4 levels. (Low, Medium, High, Very High) The effect of this is that the final projection now shows a clearer gradient of where ZIP Codes of similar densities and similar outbreak trajectories group together in the final Embedding View.

