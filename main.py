from bottle import run, get, post, request, HTTPResponse
import json

ANS_KEYWORD = "ぶんり"

def main():
    run(host="0.0.0.0", port=2222)

# 引数で受け取ったIDをTrueにする関数（引数idは文字列型）
def argIdTrue(id):
    # JSON読み込んで
    with open("status.json", "r") as f:
        data = json.load(f)

    # リクエストされたidをtrueにして
    data[id] = "true"

    # JSONに書き出し
    with open("status.json", "w") as f:
        json.dump(data, f)

# HTTPレスポンスを生成する関数
def genHTTPResponse(element):
    body = f'<html><body>{element}</body></html>'
    res = HTTPResponse(status=200, body=body)
    res.set_header('Content-Type', 'text/html')
    return res

# id 1~4 trueにセット
@post("/flag")
def setIdTrue():
    reqId = request.params.id
    print("Requested id: ", reqId)

    argIdTrue(reqId)

# JSONを文字列で返す
@get("/flag")
def getJson():
    with open("status.json", "r") as f:
        data = json.load(f)
    
    data_str = json.dumps(data)

    return data_str

# clearをtrueにセット
@post("/complete")
def setClearTrue():
    with open("status.json", "r") as f:
        data = json.load(f)
    
    data["clear"] = "true"

    with open("status.json", "w") as f:
        json.dump(data, f)

# 画像を受け取って保存
# 参考↓
# https://shuzo-kino.hateblo.jp/entry/2016/11/14/232154
@post("/img")
def setImg():
    data = request.files.data
    data.save("./", overwrite=True)

# キーワードを受信して正解していたらID1をTrueにする
# また、正解のときTrue、不正解のときFalseのHTMLレスポンスを返す
@post("/keyword")
def receiveKeyword():
    word = request.params.word

    if (word == ANS_KEYWORD):
        argIdTrue("1")

        responseText = "True"
    else:
        responseText = "False"
        
    res = genHTTPResponse(responseText)
    return res


if __name__ == "__main__":
    main()
