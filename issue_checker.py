import subprocess
import re
import os
import magic
# pip install python-magic-bin


class IssueChecker:
    @classmethod
    def run(self, filepath, check_code):
        # コンパイル失敗
        if "" != (err := compile_c_code(filepath)):
            return {
                "result": False,
                "status_code": "CAN_NOT_COMPILE",
                "output": err,
            }

        if 'skip_direct_output_check' not in check_code:
            # 出力例をそのままprintfするやつをしばくやつ
            with open(filepath) as f:
                code = exclude_comments(f.read())
                #  オプションがあった場合標準出力結果から文字を除外する
                if 'exclude' in check_code:
                    for char in check_code["exclude"]:
                        excluded_code = code.replace(char, '')
                #  正規表現にて標準出力を検証
                if self.check_stdout(excluded_code, check_code["stdout_regex"]):
                    return {
                        "result": False,
                        "status_code": "DIRECT_OUTPUT",
                        "output": code,
                    }

        # 実行チェック
        # すべての標準入力を入力
        input = ""
        if 'stdin' in check_code:
            input = " ".join(check_code["stdin"])
            # scanf("%d\n", &a)とかやり始めるやつのための例外用
            # input += "0 0 0 0 0 \n"

        try:
            completed = run_c_code(input)
            # 最終的なすべての標準出力結果
            output = completed.stdout

            # str検証
            if type(output) is not str:
                print(type(output))
                output = " "

            #  オプションがあった場合標準出力結果から文字を除外する
            if 'exclude' in check_code:
                for char in check_code["exclude"]:
                    output = output.replace(char, '')

            #  正規表現にて標準出力を検証
            if not self.check_stdout(output, check_code["stdout_regex"]):
                return {
                    "result": False,
                    "status_code": "WRONG_OUTPUT",
                    "output": output,
                }

            # 正常にチェックが完了
            return {
                "result": True,
                "status_code": "OK",
                "output": output,
            }

        except subprocess.TimeoutExpired as e:
            # 無限ループのタイムアウト処理
            return {
                "result": False,
                "status_code": "INFINITE_LOOP",
                "output": "",
            }

        except UnicodeDecodeError as e:
            with open(filepath) as f:
                # コンパイル可能だが不適切なコード
                # 基本的にIndexOutOfBoundsExceptionが該当
                code = f.read()
                return {
                    "result": False,
                    "status_code": "WRONG_CODE",
                    "output": code,
                }

    @ classmethod
    def check_stdout(self, output, regex):
        pattern = re.compile(rf'{regex}')
        result = pattern.search(output)
        if result is None:
            return False
        return True


def compile_c_code(filepath):
    # 驚くべきことだが、バイナリファイルにxxxx.cという名前をつけて提出するやつがいる
    # さらに、ディレクトリに「.c」と名前をつけるやつもいるのでディレクトリかどうかも判定する
    # Cファイルであるかどうかを確認し、そうでない場合はしばく
    if os.path.isdir(filepath):
        return "target is directory"
    elif not "C source" in magic.from_file(filepath):
        return "target is not C source"
    # コンパイル
    cmd = ["gcc", filepath]
    proc = subprocess.run(
        cmd,
        text=True,
        encoding='UTF-8',
        stderr=subprocess.PIPE,
    )
    return "" if proc.stderr == "" else proc.stderr


def run_c_code(input):
    # 実行
    cmd = "./a.exe"
    if os.name != 'nt':
        cmd = "./a.out"

    return subprocess.run(
        [cmd],
        input=input,
        text=True,
        encoding='UTF-8',
        timeout=10,
        stdout=subprocess.PIPE,
    )


def exclude_comments(code):
    # コメントを除外する
    # コメントはC言語のコードには含まれないので、そのまま残す
    array_code = code.split("\n")
    result = []
    comment_start_flag = False
    for line in array_code:
        if line.find("//") != -1:
            index = line.find("//")
            result.append(line[:index])
            continue
        if not line.find("*/"):
            comment_start_flag = False
            continue
        if not line.find("/*"):
            comment_start_flag = True
            continue
        if comment_start_flag:
            continue
        result.append(line)
    return "\n".join(result)
