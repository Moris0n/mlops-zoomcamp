import predict

ride = {
        "PULocationID": 10,
        "DOLocationID": 50,
        "trip_distance": 40
}

feautres = predict.prepare_feautres(ride)
pred = predict.predict(ride)
print(pred)
