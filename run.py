# Module version
# Execute the module version can help you create the db directly
# from ecommerce import *

# if __name__ == '__main__':
#     app.run(debug=True)

# Blueprint version
from ecommerce_blueprint_version import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
