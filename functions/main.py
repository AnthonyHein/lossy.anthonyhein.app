from encoder import Encoder

from firebase_functions import https_fn, options

from firebase_admin import initialize_app, firestore
import google.cloud.firestore

import json
import random
import typing

app = initialize_app()

def check_probability(probability: str) -> typing.Tuple[typing.Union[int, None], typing.Union[https_fn.Response, None]]:
    try:
        probability = int(probability)
    except:
        return None, https_fn.Response("Probability is not integral.", status=400)

    if probability < 1 or probability > 99:
        return None, https_fn.Response("Probability is outside {1, ..., 99}.", status=400)

    return probability, None

def get_probability(req: https_fn.Request, param="probability") -> typing.Tuple[typing.Union[int, None], typing.Union[https_fn.Response, None]]:
    probability = req.args.get(param)
    if probability is None:
        return None, https_fn.Response("No probability provided.", status=400)

    return check_probability(probability)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"https://lossy\.anthonyhein\.com$"],
        cors_methods=["get"],
    )
)
def encode(req: https_fn.Request) -> https_fn.Response:
    plaintexts = []

    i = 0
    plaintext = req.args.get(f"plaintext{i}")
    while plaintext is not None:
        plaintexts.append(plaintext)
        i += 1
        plaintext = req.args.get(f"plaintext{i}")
        
    if len(plaintexts) == 0:
        return https_fn.Response("No plaintext provided.", status=400)

    probabilities = []
    for i in range(len(plaintexts)):
        probability, error = get_probability(req, f"probability{i}")
        if error is not None:
            return error
        probabilities.append(probability)

    if sum(probabilities) > 100:
        return https_fn.Response("Probabilities sum to more than 100.", status=400)

    keys = []
    ciphertexts = []
    for plaintext in plaintexts:
        key, ciphertext = Encoder.encode(plaintext)
        if None in (key, ciphertext):
            return https_fn.Response("The plaintext may only contain printable characters.", status=400)
        keys.append(key)
        ciphertexts.append(ciphertext)

    firestore_client: google.cloud.firestore.Client = firestore.client()

    _, doc_ref = firestore_client.collection("keys").add({
        "keys": [str(key) for key in keys],
        "probabilities": [probability for probability in probabilities]})

    return https_fn.Response(json.dumps({
        "id": doc_ref.id,
        "ciphertexts": [str(ciphertext) for ciphertext in ciphertexts]}))

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"https://lossy\.anthonyhein\.com$"],
        cors_methods=["get"],
    )
)
def decode(req: https_fn.Request) -> https_fn.Response:
    id = req.args.get("id")
    if id is None:
        return https_fn.Response("No ID provided.", status=400)

    ciphertext = req.args.get('ciphertext')
    if ciphertext is None:
        return https_fn.Response("No ciphertext provided.", status=400)

    firestore_client: google.cloud.firestore.Client = firestore.client()
    doc = firestore_client.collection("keys").document(id).get()
    if not doc.exists:
        return https_fn.Response("Unrecognized ID.", status=400)

    keys = doc.to_dict().get('keys')
    if keys is None:
        return https_fn.Response("Document is corrupted; no keys provided.", status=400)

    probabilities = doc.to_dict().get('probabilities')
    if probabilities is None:
        return https_fn.Response("Document is corrupted; no probabilities provided.", status=400)

    for i in range(len(probabilities)):
        probability, error = check_probability(probabilities[i])
        if error is not None:
            return error
        probabilities[i] = probability

    firestore_client.collection("keys").document(id).delete()

    guess = random.randrange(1, 101)

    remaining = range(1, 101)
    for i, (key, probability) in enumerate(zip(keys, probabilities)):
        sample = set(random.sample(remaining, k=probability))
        if guess in sample:
            try:
                plaintext = Encoder.decode(key, ciphertext)
            except:
                return https_fn.Response("Key and ciphertext pair is not valid.", status=400)

            return https_fn.Response(json.dumps({"plaintext": plaintext}))
        remaining = list(set(remaining) - sample)

    return https_fn.Response(json.dumps({"plaintext": "DESTROYED"}))