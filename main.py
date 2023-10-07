from bottle import route, run, get, post, request
import json

def main():
    run(host="0.0.0.0", port=2222)

# id 1~4 trueにセット
@post("/flag")
def route():
    reqId = request.params.id
    print("Requested id: ", reqId)
    
    # JSON読み込んで
    with open("status.json", "r") as f:
        data = json.load(f)

    # リクエストされたidをtrueにして
    data[reqId] = "true"

    # JSONに書き出し
    with open("status.json", "w") as f:
        json.dump(data, f)

# JSONを文字列で返す
@get("/flag")
def route():
    with open("status.json", "r") as f:
        data = json.load(f)
    
    data_str = json.dumps(data)

    return data_str

# clearをtrueにセット
@post("/complete")
def route():
    with open("status.json", "r") as f:
        data = json.load(f)
    
    data["clear"] = "true"

    with open("status.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    main()
