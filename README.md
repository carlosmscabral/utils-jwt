# utils-jwt

openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem

python main.py --action jwt_only
python main.py --action all
