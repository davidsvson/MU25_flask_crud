from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)


app.config["JWT_SECRET_KEY"] = "super-hemlig-kod"
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

books = {
    1: {"id" : 1, "title" : "Python for beginners", "author" : "Timmy"},
    2: {"id" : 2, "title" : "Java for beginners", "author" : "Muamer"}
}

hashed_passwd_david = bcrypt.generate_password_hash("123456").decode('utf-8')
hashed_passwd_susan = bcrypt.generate_password_hash("pasword").decode('utf-8')


users = {
    "david" : hashed_passwd_david,
    "susan" : hashed_passwd_susan
}

@app.route("/login", methods=["POST"])
def login():
    # borde felhantera att username och pasword finns först
    username = request.json.get("username")
    password = request.json.get("password")

    stored_hashed_password = users[username]
    if not bcrypt.check_password_hash(stored_hashed_password, password):
        return jsonify({"msg" : "bad username or password"}), 401
    
    access_token = create_access_token(identity=username)
    return access_token


@app.route('/')
def hello():
    return 'Hello!'

# 1. CRUD - API - Create, Read, Update, Delete
# 2. login - JWT
 
# CREATE - POST till /books {title : , author : }
@app.route('/books', methods=['POST'])
def create_book():
    new_book_data = request.get_json()
    
    if not new_book_data or "title" not in new_book_data or "author" not in new_book_data:
        return jsonify({"error":"missing attributes"}), 404
    
    new_id = max(books.keys(), default= 0) + 1
    new_book = {
        "id" : new_id,
        "title" : new_book_data["title"],
        "author" : new_book_data["author"]
    }
    
    books[new_id] = new_book
    return jsonify(new_book), 200
    

# READ

# [R]EAD ALL BOOKS
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    #return books
    
    current_user = get_jwt_identity()
    print(f" User: {current_user}")
    return jsonify(list(books.values()))

# GET BOOK BY ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    
    if id not in books:
        return jsonify({"Error":"Book not found"}), 404
    
    return jsonify(books[id])

#UPDATE
# PUT /books/<id>
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    if id not in books:
        return jsonify({"Error":"Book not found"}), 404
    
    updated_book_data = request.get_json()
    book = books[id]
    if "title" in updated_book_data:
        book["title"] = updated_book_data["title"]
        
    if "author" in updated_book_data:
        book["author"] = updated_book_data["author"]
        
    return jsonify(book)    

#DELETE
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    if id in books:
        del books[id]
        return jsonify({"msg" : "book deleted"}), 200
    return jsonify({"Error":"Book not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)