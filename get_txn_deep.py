from iota import TryteString
from iota.trits import int_from_trits
import requests
import json
import threading
import ast
import datetime

NODE_URL = "https://pow.iota.community:443"
COORDINATOR_ADDR = "EQSAUZXULTTYZCLNJNTXQTQHOMOFZERHTCGTXOLTVAHKSA9OGAZDEKECURBRIXIJWNPFCQIOVFVVXJVD9DGCJRJTHZ"
hash_transatcion = "SJXZIEIUAEIITGZEZGAGRMCFNFLYVAFC9NPQPOEP9KPGMH9UHDAXZIUD9CMRD9RXSMMVGZUDORX999999"
list_milestone = []

def get_txn_tag(hash_txn):
    data = {'command': 'getTrytes', 'hashes':[hash_txn]}
    headers = {'Content-type': 'application/json', 'X-IOTA-API-Version': '1'}
    r = requests.post(NODE_URL, data=json.dumps(data), headers=headers)

    if r.status_code == requests.codes.ok:
        json_response = json.loads(r.text)
        return json_response["trytes"][0][2295:2322]

def get_current_milestone_index():
    data = {'command': 'getNodeInfo'}
    headers = {'Content-type': 'application/json', 'X-IOTA-API-Version': '1'}
    r = requests.post(NODE_URL, data=json.dumps(data), headers=headers)

    # latestSolidSubtangleMilestoneIndex
    if r.status_code == requests.codes.ok:
        json_node_info = json.loads(r.text)
        return int(json_node_info["latestSolidSubtangleMilestoneIndex"])

    return 0

def get_child_txn_list(hash_txn):
    url = NODE_URL
    data = {'command': 'findTransactions', 'approvees':[hash_txn]}
    headers = {'Content-type': 'application/json', 'X-IOTA-API-Version': '1'}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    if r.status_code == requests.codes.ok:
        txn_hash_child = json.loads(r.text)
        return txn_hash_child["hashes"]
    else:
        return []

def find_milestone(hash_txn):
    print(datetime.datetime.now().strftime("%m-%d %H:%M") + " Child transaction: " + hash_txn)
    data = {'command': 'getTrytes', 'hashes':[hash_txn]}
    headers = {'Content-type': 'application/json', 'X-IOTA-API-Version': '1'}
    r = requests.post(NODE_URL, data=json.dumps(data), headers=headers)

    if r.status_code == requests.codes.ok:
        if COORDINATOR_ADDR[:80] in r.text:
            tag_milestone = get_txn_tag(hash_txn)
            index_milestone = int_from_trits(TryteString(tag_milestone).as_trits())

            return index_milestone

        return 0

def get_iri_depth(hash_txn):
    list_hash_child = get_child_txn_list(hash_txn)
    while len(list_hash_child) > 0:
        index_milestone = find_milestone(list_hash_child[0])
        if index_milestone != 0:
            # Compare with latest milestone
            current_milestone_index = get_current_milestone_index()
            iri_depth = current_milestone_index - index_milestone
            return iri_depth

        next_child_list = get_child_txn_list(list_hash_child[0])
        list_hash_child.remove(list_hash_child[0])
        list_hash_child = list_hash_child + next_child_list

iri_depth = get_iri_depth(hash_transatcion)
print("IRI depth: " + str(iri_depth))
