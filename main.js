const dataUrl = "embeddings_umap.csv";

// =============================================================================
// THREE VIEWS - EMBEDDING + MAP + TIMELINE WITH SHARED SELECTION
// UPDATED: Full width + Legends
// =============================================================================

const spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {"url": dataUrl},
    
    //  ONE selection parameter for ALL THREE views
    "params": [{
        "name": "selected",
        "select": {
            "type": "point",
            "fields": ["ZIP Code"],
            "on": "click",
            "clear": false   //  prevents accidental wipeout
        }
    }],

    "hconcat": [
        // LEFT: UMAP (BIGGER to fill space)
        {
            "width": 700,    // ← Changed from 500
            "height": 600,   // ← Changed from 500
            "title": {
                "text": "UMAP Projection",
                "fontSize": 16,
                "fontWeight": "bold"
            },
            "mark": "circle",
            "encoding": {
                "x": {
                    "field": "UMAP_1", 
                    "type": "quantitative",
                    "title": "UMAP Dimension 1"
                },
                "y": {
                    "field": "UMAP_2", 
                    "type": "quantitative",
                    "title": "UMAP Dimension 2"
                },
                "color": {
                    "field": "Population_Stratum", 
                    "type": "nominal",
                    "title": "Population Density",  // ← Legend title
                    "legend": {                     // ← ADD LEGEND
                        "orient": "bottom",
                        "titleFontSize": 13,
                        "labelFontSize": 11,
                        "symbolSize": 100
                    }
                },
                "opacity": {
                    "condition": {"param": "selected", "value": 1},
                    "value": 0.2
                },
                "size": {
                    "condition": {"param": "selected", "value": 200},
                    "value": 50
                },
                "tooltip": [
                    {"field": "ZIP Code", "type": "nominal", "title": "ZIP Code"},
                    {"field": "Population_Stratum", "type": "nominal", "title": "Density"},
                    {"field": "UMAP_1", "type": "quantitative", "title": "UMAP 1", "format": ".2f"},
                    {"field": "UMAP_2", "type": "quantitative", "title": "UMAP 2", "format": ".2f"}
                ]
            }
        },
        
        // RIGHT: Map and Timeline stacked (BIGGER)
        {
            "vconcat": [
                // TOP RIGHT: Map
                {
                    "width": 550,    // ← Changed from 400
                    "height": 300,   // ← Changed from 250
                    "title": {
                        "text": "Geographic Locations",
                        "fontSize": 16,
                        "fontWeight": "bold"
                    },
                    "mark": "circle",
                    "encoding": {
                        "longitude": {"field": "Longitude", "type": "quantitative"},
                        "latitude": {"field": "Latitude", "type": "quantitative"},
                        "color": {
                            "field": "Population_Stratum", 
                            "type": "nominal",
                            "legend": {              // ← ADD LEGEND for map too
                                "orient": "right",
                                "titleFontSize": 12,
                                "labelFontSize": 10,
                                "symbolSize": 80,
                                "title": "Density"
                            }
                        },
                        "opacity": {
                            "condition": {"param": "selected", "value": 1},
                            "value": 0.2
                        },
                        "size": {
                            "condition": {"param": "selected", "value": 150},
                            "value": 30
                        },
                        "tooltip": [
                            {"field": "ZIP Code", "type": "nominal", "title": "ZIP Code"},
                            {"field": "Population_Stratum", "type": "nominal", "title": "Density"}
                        ]
                    },
                    "projection": {"type": "mercator"}
                },
                
                // BOTTOM RIGHT: Timeline (NOW REACTS TO UMAP & MAP)
                {
                    "width": 550,    // ← Changed from 400
                    "height": 280,   // ← Changed from 230
                    "title": {
                        "text": "Case Rates Over Time (Filtered by Selection)",
                        "fontSize": 16,
                        "fontWeight": "bold"
                    },

                    // Still listens to UMAP + Map
                    "transform": [
                        { "filter": { "param": "selected" } }
                    ],

                    "mark": "line",

                    "encoding": {
                        "x": {
                            "field": "Week End",
                            "type": "temporal",
                            "title": "Date",
                            "axis": {"labelAngle": -45}
                        },

                        //  NO AGGREGATE — ZIP IS PRESERVED
                        "y": {
                            "field": "Case Rate - Cumulative",
                            "type": "quantitative",
                            "title": "Cumulative Case Rate"
                        },

                        // Each ZIP gets its own line → now clickable
                        "detail": {
                            "field": "ZIP Code",
                            "type": "nominal"
                        },

                        "color": {
                            "field": "Population_Stratum",
                            "type": "nominal",
                            "title": "Population Density",  // ← Legend title
                            "legend": {                     // ← ADD LEGEND
                                "orient": "right",
                                "titleFontSize": 12,
                                "labelFontSize": 10,
                                "symbolSize": 80
                            }
                        },

                        "tooltip": [
                            { "field": "ZIP Code", "type": "nominal", "title": "ZIP Code" },
                            { "field": "Week End", "type": "temporal", "title": "Date", "format": "%b %d, %Y" },
                            { "field": "Case Rate - Cumulative", "type": "quantitative", "title": "Case Rate", "format": ",.0f" }
                        ]
                    }
                }

            ]
        }
    ]
};

vegaEmbed('#viz', spec, {actions: false}).then(() => {
    console.log("✅ All 3 views loaded with full width + legends!");
    console.log("🎯 Click any point in UMAP or map");
    console.log("   → Both views highlight together");
    console.log("   → Timeline now updates from UMAP & Map");
}).catch(console.error);

