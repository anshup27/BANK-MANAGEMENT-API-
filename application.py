from flask import Flask, jsonify, redirect
from flask_restful import Api, MethodNotAllowed, NotFound
from flask_cors import CORS
from util.common import domain, port, prefix, build_swagger_config_json
from resources.swaggerConfig import SwaggerConfig
from bankResource import Accounts, ApplyInterest,Deposit, Statement,Transactions,Account, UpdateCustomer,Withdraw,BlockAccount,CloseAccount,init_db
from flask_swagger_ui import get_swaggerui_blueprint


# ============================================
# Main
# ============================================




application = Flask(__name__)
app = application
app.config['PROPAGATE_EXCEPTIONS'] = True
CORS(app) 
api = Api(app, prefix=prefix, catch_all_404s=True)


init_db()
#mongo_uri=os.getenv("MONGO_URI")
#mongo_uri=os.getenv("MONGO_DB")
#client=MongoClient("MONGO_URI")
#db=client["MONGO_DB"]
#Student=db["flask"]

# ============================================
# Swagger
# ============================================
build_swagger_config_json()
swaggerui_blueprint = get_swaggerui_blueprint(
    prefix,
    f'http://{domain}:{port}{prefix}/swagger-config',
    config={
        'app_name': "Flask API",
        "layout": "BaseLayout",
        "docExpansion": "none"
    },
)
app.register_blueprint(swaggerui_blueprint)

# ============================================
# Error Handler
# ============================================


@app.errorhandler(NotFound)
def handle_method_not_found(e):
    response = jsonify({"message": str(e)})
    response.status_code = 404
    return response


@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed_error(e):
    response = jsonify({"message": str(e)})
    response.status_code = 405
    return response


@app.route('/')
def redirect_to_prefix():
    if prefix != '':
        return redirect(prefix)


# ============================================
# Add Resource
# ============================================
# GET swagger config
api.add_resource(SwaggerConfig, '/swagger-config')
# GET Student
api.add_resource(Accounts, "/accounts")
api.add_resource(Account, "/accounts/<int:id>")
api.add_resource(Deposit, "/accounts/deposit")
api.add_resource(Withdraw, "/accounts/withdraw")
api.add_resource(Transactions, "/accounts/<int:id>/transactions")
api.add_resource(BlockAccount, "/accounts/block")
api.add_resource(CloseAccount, "/accounts/close")
api.add_resource(UpdateCustomer, "/accounts/<int:id>/customer")
api.add_resource(ApplyInterest, "/accounts/interest")
api.add_resource(Statement, "/accounts/<int:id>/statement")


if __name__ == '__main__':
    app.run(debug=True)
