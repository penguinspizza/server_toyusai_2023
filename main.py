from bottle import run, get, post, request, HTTPResponse
import json
import subprocess
import os

# YOLOはサーバ上のどこかのディレクトリにgit cloneして使うため、クローン先へのパスを記述する(絶対パス)
YOLO_DETECT_PY_PATH = "C:\\Users\\ymd\\Desktop\\app_dev_toyusai2023\\yolo_learning\\yolov5\\detect.py"

# 画像認識に通す画像が入っているディレクトリ(絶対パス)
YOLO_SOURCE_DIR_PATH = "C:\\Users\\ymd\\Desktop\\app_dev_toyusai2023\\server_toyusai_2023\\img\\"

# モデルのパス(絶対パス)
YOLO_MODEL_PATH = "C:\\Users\\ymd\\Desktop\\app_dev_toyusai2023\\server_toyusai_2023\\models\\best.pt"

# 結果を保存するディレクトリ(絶対パス)
YOLO_RESULT_DIR_PATH = "C:\\Users\\ymd\\Desktop\\app_dev_toyusai2023\\server_toyusai_2023\\results\\exp"

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

# HTTPリダイレクトレスポンスを生成する関数
def genHTTPRedirectResponse(url):
    res = HTTPResponse(status=302)
    res.set_header('Location', url)
    return res

# id 1~4 trueにセット
@post("/flag")
def setIdTrue():
    reqId = request.params.id
    print("Requested id: ", reqId)

    argIdTrue(reqId)

# ライントレーサーがゴールしたらid2をtrueにする
@post("/goal")
def setIdTrue():
    argIdTrue("2")

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
    # 画像を保存
    data = request.files.data
    data.save("./img/", overwrite=True)

    # 画像認識実行
    res = subprocess.run([
        "python",
        YOLO_DETECT_PY_PATH,
        "--source",
        f'{YOLO_SOURCE_DIR_PATH}{data.filename}',
        "--img",
        "640",
        "--save-txt",
        "--save-conf",
        "--weight",
        YOLO_MODEL_PATH,
        "--name",
        YOLO_RESULT_DIR_PATH
    ], shell=True, stdout=subprocess.PIPE, text=True)

    if (res.returncode != 0):
        return "画像認識に失敗しました"

    # 対象のディレクトリパスを指定
    directory_path = './results/'

    # ディレクトリ内のサブディレクトリをリストアップ
    subdirectories = [name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]

    # ディレクトリ名から数字を抽出してソート
    numeric_directories = sorted(
        (int(subdir[len('exp'):]) for subdir in subdirectories if subdir.startswith('exp') and subdir[len('exp'):].isdigit()),
        reverse=True  # 逆順にソート
    )

    if numeric_directories:
        # 最大の数字を持つディレクトリを取得
        latest_directory_number = numeric_directories[0]
        latest_directory_path = os.path.join(directory_path, f'exp{latest_directory_number}')
        print(f"一番数字の大きいディレクトリのパス: {latest_directory_path}")
    else:
        print("連番のディレクトリが見つかりませんでした。")

    # 拡張子を除いたファイル名を取得
    non_extension_filename = data.filename.split('.')[0]

    # 結果が書かれたテキストファイルのパス
    latest_result_txt_path = f'{latest_directory_path}/labels/{non_extension_filename}.txt'

    print(f"一番数字の大きいディレクトリにあるテキストファイルのパス: {latest_result_txt_path}")

    # ファイルからテキストを読み込む
    try:
        with open(latest_result_txt_path, 'r') as file:
            lines = file.read().split('\n')
    except FileNotFoundError:
        print("1つもBを検出できませんでした")
        return

    # テキストを2次元配列に変換
    data = [line.split() for line in lines if line]

    # 各行ごとに要素を浮動小数点数に変換
    data = [[float(element) for element in line] for line in data]

    # 2次元配列の内容を表示（テスト用）
    print("結果")
    for row in data:
        print(row)

    # 閾値を設定
    threshold = 0.60

    # 2次元配列内で最大の一番右の要素を持つ行を見つける
    max_right_element = float('-inf')  # 最大の右要素を無限小の値で初期化
    max_left_element = None  # 最大の右要素を持つ行の左要素を格納する変数

    for row in data:
        right_element = row[-1]  # 一番右の要素を取得
        if right_element > max_right_element and right_element >= threshold:
            max_right_element = right_element
            max_left_element = row[0]  # 最大の右要素を持つ行の左要素を格納

    # 結果を出力
    if max_left_element is not None:
        print("一番右の要素が閾値を満たす最大の行の一番左の要素:", max_left_element)
        # 正解なのでフラグをtrueにする
        argIdTrue("4")
    else:
        print("該当する行が存在しません。")

# キーワードを受信して正解していたらID1をTrueにする
# また、正解のときTrue、不正解のときFalseのHTMLレスポンスを返す
# TODO https://qiita.com/tomotaka_ito/items/377b2287e71ecd8b4f16 ここを参考に静的ファイルの配信を実装 2023/10/21
@post("/keyword")
def receiveKeyword():
    word = request.params.word
    print("input word:", word)

    if (word == ANS_KEYWORD):
        argIdTrue("1")

        url = "http://192.168.0.32/escape_room/ok.html"
    else:
        url = "http://192.168.0.32/escape_room/ng.html"
        
    res = genHTTPRedirectResponse(url)
    return res


if __name__ == "__main__":
    main()
