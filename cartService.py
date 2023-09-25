# Name: Monica Morrison
# CMSC 455
import requests 
from flask import Flask, jsonify, request

app = Flask(__name__)

#Set variable to product service
baseURL = 'http://127.0.0.1:5000' 
# Three users with empty carts
carts = [
    {"userID": 1, "cart": {}},
    {"userID": 2, "cart": {}},
    {"userID": 3, "cart": {}}
]

def get_products(product_id):
    response = requests.get(f'http://127.0.0.1:5000/products/{product_id}')
    data = response.json()
    return data

# /cart/{user id} (GET): Retrieve the current contents of a user’s shopping cart, including prod-
# uct names, quantities, and total prices.
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    userCart = next((userCart for userCart in carts if userCart["userID"] == user_id), None)
    if userCart:
        return jsonify({"User": userCart})
    else:
        return jsonify({"error": "User cannot be found"}), 400
    
# /cart/{user id}/add/{product id} (POST): Add a specified quantity of a product to the user’s cart.
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_product(user_id, product_id):
    
    data = request.json
    if 'quantity' in data:
        quant = data['quantity']
        userCart = next((user for user in carts if user["userID"] == user_id), None)
        if userCart:
            #Does product exist in cart
            if product_id in userCart['cart']:
                #Update quant 
                userCart['cart'][product_id]['quantity'] += quant
                response = requests.post(f'{baseURL}/products/take/{product_id}', json={"quantity": quant})
                
                if response.status_code == 400:
                    userCart['cart'][product_id]['quantity'] -= quant
                    return jsonify({"message": "Not enough products in the inventory"})

                responseGet = requests.get(f'{baseURL}/products/{product_id}')
                productData = responseGet.json()
                #get product because the product obj has multiple objs within 
                product = productData.get('product')
                #get the name and price from the product obj
                price = product['price']

                #get the total price of item in cart
                totalPrice = price * userCart['cart'][product_id]['quantity']
                userCart['cart'][product_id]['total price']=totalPrice
            
            else:
                
                response = requests.post(f'{baseURL}/products/take/{product_id}', json={"quantity": quant})
                if response.status_code == 400:
                    return jsonify({"message": "Not enough products in the inventory"})
                productData = get_products(product_id)
                #get product because the product obj has multiple objs within 
                product = productData.get('product')
                    
                #get the name and price from the product obj
                name = product['name']
                price = product['price']
                    
                #get the total price of item in cart
                totalPrice = price * quant
            
                userCart['cart'][product_id] = {
                    "name": name,
                    "price": price,
                    "quantity": quant,
                    "total price": f"${totalPrice}"
                }
            return jsonify({"message": f"Added {data['quantity']} product: {product_id} to user: {user_id}'s cart"})
        else:
            return jsonify({"error": "Cart does not exist"}), 400
    else:
        return jsonify({"error": "Quantity not given"}), 400
    
        
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_product(user_id, product_id):
    
    data = request.json
    if 'quantity' in data:
        #get quantity from req body
        quant = data['quantity']
        
        userCart = next((user for user in carts if user["userID"] == user_id), None)
        if userCart:
            #removing product --this product does exist
            if product_id in userCart['cart']:
                #if quantity in cart is greater than quant req
                if  userCart['cart'][product_id]['quantity'] > quant:
                    userCart['cart'][product_id]['quantity'] -= quant
                    quant = userCart['cart'][product_id]['quantity']
                    response = requests.post(f'{baseURL}/products/return/{product_id}', json={"quantity": quant})                
                    # if response.status_code == 400:
                    #     userCart['cart'][product_id]['quantity'] += quant
                    #     return jsonify({"message": "???Not enough products in the inventory"})
                                                 
                    productData = get_products(product_id)
                    product = productData.get('product')
                    price = product['price']
                    name = product['name']
                    #Find the reduced total 
                    totalPrice = price * quant
                    
                    userCart['cart'][product_id] = {
                        "name": name,
                        "price": price,
                        "quantity": quant,
                        "total price": f"${totalPrice}"
                    }
                                   
                    return jsonify({"message": f"Removed {data['quantity']} product: {product_id} from user cart {user_id}"})
                #amount is cart is 0 
                elif userCart['cart'][product_id]['quantity'] < quant:
                    print(userCart['cart'][product_id]['quantity'])
                    return jsonify({"error": "The removal quantity exceeds the amount inside cart"}), 400
                else:
                    print("2nd case", userCart['cart'][product_id]['quantity'])
                    #product quantity is empty
                    response = requests.post(f'{baseURL}/products/return/{product_id}', json={"quantity": quant})
                    #update
                    userCart['cart'][product_id]['quantity'] += quant
                    ("update2", userCart['cart'][product_id]['quantity'])
                    #delete the entire product inside cart
                    del userCart['cart'][product_id]
                    return jsonify({"message": "All quantity of product has been removed"})
            else:
                return jsonify({"error": "This product is not in the cart"}), 400
        else:
            return jsonify({"error": "User was not found"}), 400
    else:         
        return jsonify({"error": "Quantity was not given"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
 