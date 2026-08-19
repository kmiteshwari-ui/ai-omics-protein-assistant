import streamlit.components.v1 as components


def show_structure(pdb_url):
    html = f"""
    <html>
    <head>
        <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    </head>

    <body>

    <div
        id="viewer"
        style="width:100%; height:500px; position:relative;">
    </div>

    <script>
        let viewer = $3Dmol.createViewer(
            "viewer",
            {{
                backgroundColor: "white"
            }}
        );

        fetch("{pdb_url}")
            .then(response => response.text())
            .then(data => {{

                viewer.addModel(
                    data,
                    "pdb"
                );

                viewer.setStyle(
                    {{}},
                    {{
                        cartoon: {{
                            color: "spectrum"
                        }}
                    }}
                );

                viewer.zoomTo();
                viewer.render();
            }});
    </script>

    </body>
    </html>
    """

    components.html(
        html,
        height=520
    )
