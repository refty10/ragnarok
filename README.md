# Ragnarok ver.1.0.3

[**Githab**](https://github.com/refty10/ragnarok)

[**Download**](https://drive.google.com/drive/folders/16o2WW8J0-N9kyPe4jo3diD37PKiogDmX?usp=sharing)

C 言語採点自動化ソフトウェア

> _The end of human power.
> This is "Ragnarok"..._

## 仕様について

### 言語

- Python3.9.6

- libmagic のインストールがいるっぽい
  - [libmagic](https://formulae.brew.sh/formula/libmagic)

requirements.txt

```txt=
python-magic==0.4.24
python-magic-bin==0.4.14
pandas==1.3.1
```

### 開発環境

- windows
- mac でも動作するようには作ってる

### 実行結果

- SQLite に実行結果が保存されます
- 各自でクエリを叩くなりして、欲しいデータを抽出してください

### 各ディレクトリ

- **./data**: Moodle からダウンロードした生のデータ。生徒情報の入った`students.csv`のデータ
- **./db**: `ragnarok.db`という名前で SQLite のデータが入っています
- **./settings**: 採点をするための設定 JSON ファイルが入っています
- **./temp**: `./data`から採点ができる状態にディレクトリ及びファイルを整理したデータが入っています

### 各 Python ファイル

- **calculate_rating**: 採点後、生徒の評点を自動計算し SQLite に保存します
- **color_print**: 俺が作ったコンソール上に色付きで標準出力できるライブラリ
- **database**: SQLite のコネクタ＆リポジトリ。割とコードが雑。
- **db_maker.py**: 新規で SQLite データベースを作成するときに使います
- **dir_maker**: `./data`の生データを採点できる状態に整理し`./temp`にデータを生成します
- **issue_checker**: 採点を行うコード
- **ragnarok**: Ragnarok のエントリポイント。基本この Python ファイルを実行する

## 使い方

> コマンド`python *.py`について
> Mac の場合は`python3 *.py`で実行してください

### 初期設定

1. `./db`に`ragnarok.db`がある場合削除してください
2. `./data`に`students.csv`を作成してください
   students.csv

```csv=
学籍番号,学生氏名
K21002,Firstname name
K21003,Firstname name
K21005,Firstname name
K21006,Firstname name
...
```

3. `python db_maker.py`
4. 以上です

### 採点の仕方

> Moodle の設定で「提出フォルダに入れてダウンロード」をチェックを入れること
> <img src="https://gyazo.com/da2945042da0412b6d5e619a9dafe80e.png">

1. Moodle から zip ファイルをダウンロード・解凍して`./data`に保存してください（フォルダ名を`row_subject_*_*`と言った感じにリネームしておくといいです）
2. `./settings`に`subject_*_*.json`を作成してください（設定ファイルについては後述）
3. `python ragnarok.py subject_*_*.json`もしくは`python ragnarok.py`
   - `python ragnarok.py`で実行した場合
   ```=
   PS F:\Python\Ragnarok> python .\ragnarok.py
   subject_02_homework.json
   subject_03_practice.json
   subject_08_practice.json
   > > Please Select Setting : subject_02_homework.json
   ```
   と言った感じに設定ファイルを聞いてくるので、表示された設定ファイルを指定してください（.json も必要です）
   - 起動引数オプション `--skip`
     - この起動引数オプションを付与した場合、dir_maker を実行しません
     - temp 内に存在するディレクトリのみで検証を行います
     - 実行済みの`temp/k*****`データを削除したのち本オプションを付与することで削除した生徒をスキップできます
4. ゴニョゴニョいっぱい出てきて終わり（少し時間がかかります）
5. SQLite に実行結果が保存されているので採点ミス等の問題が無いかチェックしてください（submits テーブルに保存されています）
6. 採点ミス等が見つかった場合、直接 SQLite の編集を行って修正をしてください
7. `python calculate_rating.py subject_*_*.json`もしくは`python calculate_rating.py`

   - `python calculate_rating.py`で実行した場合

   ```=
   PS F:\Python\Ragnarok> python .\ragnarok.py
   subject_02_homework.json
   subject_03_practice.json
   subject_08_practice.json
   > > Please Select Setting : subject_02_homework.json
   ```

8. 以上で終了です。（採点結果は、ratings テーブルに保存されています）

### dir_maker を単体で使いたい！

`python dir_maker.py ./data/dirname`で実行できます。

> 救済措置や最終課題等など、Zip ファイルや各生徒のめちゃくちゃなディレクトリ構造を整理しきれいな状態でファイルを操作したいときに使ってください。

### 評点計算(calculate_rating.py)について

設定の`"required_issue_count": number`を参照して評点計算を行います

#### Status_Code による加点

- OK: **+1**
  - 正常に動作したとして加点
- WRONG_OUTPUT: **+0.5**
  - コンパイルが通るが検証にパスできなかったとして加点
- INFINITE_LOOP: **+0.5**
  - コンパイルが通るが検証にパスできなかったとして加点
- CAN_NOT_COMPILE: **+0.25**
  - 提出点として少し加点
- WRONG_CODE: **+0.25**
  - 提出点として少し加点
- DIRECT_OUTPUT: **0**
  - printf()を用いて回答をそのまま出力している場合
  - なめているので０点
- NOT_SUBMITTED: **+0**
  - 提出がなかったとして加点なし
- CAN_NOT_FIND_SOURCECODE: **+0**
  - 提出がなかったとして加点なし

#### 評点の計算式

Status_Code による加点の合計を`required_issue_count`で割り算を行います

**例**
`required_issue_count: 5`

必須提出が 5 つ
必須提出でないものが 1 つ(00_06 がそれだと仮定)

- 00_01: OK
  - +1
- 00_02: OK
  - +1
- 00_03: OK
  - +1
- 00_04: OK
  - +1
- 00_05: OK
  - +1
- 00_06: WRONG_OUTPUT
  - +0.5

**基本計算**

```=
5.5 / 5 = 110
```

**加点計算**

> Subject ごとの最大加点数を「**+25**」と定義

ここから加点分の計算を行う

> 今回の最大提出数は 5 つなので最大理論値は：**120**

100 点からのオーバーフロー 1 点あたりの点数を計算

```=
25 / (120 - 100) = 1.25
```

加点分を計算

```=
1.25 * (110 - 100) = 12.5
```

加点分を 100 点に追加(繰り上げ計算とする)

```=
(int) 100 + 12.5 = 113
```

**最終結果: 113 点**

### setting.json の記述の仕方

#### setting.json のサンプル

subject_08_practice.json

```json=
{
  "dir_path": "data/row_subject_08_practice",
  "subject": {
    "id": "08_practice",
    "title": "第8回_演習問題"
  },
  "required_issue_count": 7,
  "issues": [
    {
      "id": "08_01",
      "title": "rectangle",
      "filename_regex": ".*_01.*.c",
      "check_code": {
        "stdin": ["2", "6"],
        "exclude": ["\n", " ", "　"],
        "stdout_regex": "#{12}"
      }
    },
    {
      "id": "08_02",
      "title": "whileLoop",
      "filename_regex": ".*_02.*.c",
      "check_code": {
        "stdin": ["3"],
        "exclude": ["\n", " ", "　"],
        "stdout_regex": ".*3210.*"
      }
    },
    {
      "id": "08_03",
      "title": "hello10",
      "filename_regex": ".*_03.*.c",
      "check_code": {
        "exclude": ["\n", " ", "　", ",", "World", "world", "!"],
        "stdout_regex": "(Hello){10}"
      }
    },
    {
      "id": "08_04",
      "title": "calcWhile",
      "filename_regex": ".*_04.*.c",
      "check_code": {
        "stdin": ["20", "-12", "0"],
        "stdout_regex": "8"
      }
    },
    {
      "id": "08_05",
      "title": "tillzero",
      "filename_regex": ".*_05.*.c",
      "check_code": {
        "stdin": ["1050"],
        "stdout_regex": ".*-50.*"
      }
    },
    {
      "id": "08_06",
      "title": "tillzero2",
      "filename_regex": ".*_06.*.c",
      "check_code": {
        "stdin": ["100", "0"],
        "stdout_regex": ".*取引終了.*"
      }
    },
    {
      "id": "08_07",
      "title": "tillzero3",
      "filename_regex": ".*_07.*.c",
      "check_code": {
        "stdin": ["-100", "0"],
        "stdout_regex": ".*無効.*"
      }
    },
    {
      "id": "08_08",
      "title": "triangle",
      "filename_regex": ".*_08.*.c",
      "check_code": {
        "stdin": ["5"],
        "exclude": ["\n", " ", "　"],
        "stdout_regex": "\\*{15}"
      }
    }
  ]
}
```

#### 各プロパティの説明

```json=
{
  "dir_path": "data/row_subject_08_practice",
  "subject": {
    "id": "08_practice",
    "title": "第8回_演習問題"
  },
  "required_issue_count": 7,
  "issues": [{issue_object}, {issue_object}]
}
```

- **dir_path**: [required] Model からダウンロードしたデータの場所を指定してください
- **subject**
  - **id**:[required] subject の id を指定してください
  - **title**:[required] subject の title を指定してください
- **required_issue_count**: [required] subject ごとにおける提出されるべき課題の数を指定してください
  > 例えば、通常課題が 7 個でチャレンジ課題が 1 個の合計 8 個の課題提出が予想されるとするならば、必ず提出されなければならない数である「7」を指定する
- **issues**: [required] Array of issue_object

**issue_object**

```json=
{
  "id": "08_01",
  "title": "rectangle",
  "filename_regex": ".*_01.*.c",
  "check_code": {
    "stdin": ["2", "6"],
    "exclude": ["\n", " ", "　"],
    "stdout_regex": "#{12}",
    // これは基本使わない↓
    "skip_direct_output_check": true
  }
}
```

- **id**: [required]: 課題の id を指定してください
- **title**: [required]: 課題の title を指定してください
- **filename_regex**: [required]: 提出されるファイルから予想されるファイル名を正規表現で指定してください
  > できる限り、限界までゆる～い正規表現を使用してください
  > ファイルが１個とかなら`.*.c`でいいです
  > だたし、正規表現を行うファイルパスは絶対パスになるためゆるすぎるのも注意が必要です
- **check_code**: コード検証の設定
  - **stdin**: [optional]: 標準入力が必要である場合に文字列の配列として指定してください
    > この時、指定する標準入力は順に入力した時に正常終了できるように指定を行ってください
    > ここで指定した標準入力を行ってもプログラムが正常に終了しない場合は無限ループ陥るコードを書いたものとして"INFINITE_LOOP"として処理します
  - **exclude**: [optional]: 標準出力された文字列から削除する文字列を配列で指定してください
    > 場合によっては開業コードやスペース・特定の文字列といった文字列を削除してからのほうが"stdout_regex"で指定する正規表現の指定が楽になると思います
  - **stdout_regex**: [required]: 最終的に出力される標準出力（exclude に指定がある場合、指定された文字列が削除された状態）を正規表現にて検証します
    > ここで、正規表現にマッチしない場合"WRONG_OUTPUT"として処理されます
  - **skip_direct_output_check**: [optional]: printf()等を用いて直接回答を出力しているコード検証をスキップします。指定する場合、値は`true`を指定する。
  - ver.1.03 で判定にコメント文が含まれないようになりました。
    > 一部の問題で「Hello, World」をそのまま出力するような特殊なケースで誤検知されてしまう場合などに使用してください。

#### 正規表現を記述する際の注意点

[正規表現のチェックツール](https://regexr.com)

[JSON の文字エスケープツール](https://ja.infobyip.com/jsonencoderdecoder.php)

[正規表現でエスケープが必要な文字一覧表](https://qiita.com/katsukii/items/1c1550f064b4686c04d4)

JSON 内に正規表現を記述するため正規表現で使用する文字列に JSON で文字エスケープが必要な文字があった場合その文字をエスケープする必要があります。

- 正規表現を`.*08_01.*\.c`と指定したい場合
  - `.*08_01.*\\.c`と入力
- 正規表現を`\*{15}`と指定したい場合
  - `\\*{15}`と入力

例えば：こんな問題のとき
<img width=400 src="https://gyazo.com/89044167de99a0e34054db6016b64b0f.png">

```json=
{
  "id": "02_04",
  "title": "lineA",
  "filename_regex": ".*02_04.*\\.c",
  "check_code": {
    "exclude": ["\n", " ", "　"],
    "stdout_regex": "\\*\\/\\\\\\/\\\\\\/-{5}\\\\\\/\\\\"
  }
}
```

`"exclude": ["\n", " ", " "]`で改行とスペースを削除して標準出力結果はこうなる

> `*/\/\/-----\/\`

これにマッチングする正規表現は

> `\*\/\\\/\\\/-{5}\\\/\\`

なのでこうなる

> `"stdout_regex": "\\*\\/\\\\\\/\\\\\\/-{5}\\\\\\/\\\\"`

### Status Code 一覧

| Code                    | Result | 説明                                                                              |
| ----------------------- | ------ | --------------------------------------------------------------------------------- |
| OK                      | True   | 正常に採点できました                                                              |
| NOT_SUBMITTED           | False  | この subject で提出がありませんでした                                             |
| CAN_NOT_FIND_SOURCECODE | False  | この subject で提出が行われましたが、<br>該当のファイルを見つけることができません |
| CAN_NOT_COMPILE         | False  | 該当のソースコードをコンパイルできませんでした                                    |
| WRONG_OUTPUT            | False  | 提出されたソースコードからは、<br>正しい結果を得ることができませんした            |
| WRONG_CODE              | False  | 提出されたソースコードから、<br> 致命的なエラーが検出されました                   |
| INFINITE_LOOP           | False  | 無限ループに陥りました                                                            |
| DIRECT_OUTPUT           | False  | ソースコード上に回答を直接出力する不正を検知しました                              |

## パッチノート

### ver1.0.0（β 版からの変更点）

- setting.json の記述方法が変わりました
- dir_maker を Update しました
  - フォルダに入れた状態で Zip にするやからを対処
    > その場合
    > `temp/k****/zip_filename/****.c`といった感じになって CAN_NOT_FIND_SOURCECODE になってた。
    > これを修正
  - フォルダ名に「.c」「.zip」をつけるやからを対処
- calculate_rating.py を実装
- 無限ループに陥るやからの対処をしました
  - 現状、実行時間３秒を超えた場合にタイムアウトとして処理ます
    - 場合によっては setting.json で時間を変更できるようにしたほうがいいか？
  - 無限ループした際は、INFINITE_LOOP としての Status Code を付与します
- TODO: main.c 対策

### ver1.0.1

- 起動引数にオプション`--skip`を追加
  - make_dir の処理をスキップします
  - 一部、手動で temp フォルダ内を修正したい場合に使用してください
- SQL インジェクション対策を強化
- コンパイル対象となったファイルを表示するようにしました
  - ゆるすぎる正規表現でミスが無いか確認してください
- dir_maker を単体で操作できるコンソールを用意しました
  - `python dir_maker filepath`で使用できます。

### ver1.0.2

- `DIRECT_OUTPUT`を追加しました
  - `printf()`等で直接、回答を出力する輩をしばきます
  - アルゴリズムとしては、出力の正規表現検証のアルゴリズムをソースコードにも適応します。
  - 一部「Hello, World」をそのまま出力するような特殊なケース以外で、誤検知されてしまう場合、`skip_direct_output_check`オプションでこの検証を無効にすることが可能です

### ver1.0.3

- `DIRECT_OUTPUT`の判定にコメント文が含まれないように変更しました。
- `WRONG_CODE`が追加されました。
  - 判定中にエラーが発生するコードに対してこのステータスコードを使用します。
  - 現在、確認されているエラーは「OutOfBoundsException」で、参照範囲外の配列にアクセスするコードに対してこのステータスコードが付与されます。
