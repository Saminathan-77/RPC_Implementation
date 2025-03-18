import grpc
import code_execution_pb2
import code_execution_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = code_execution_pb2_grpc.CodeExecutionServiceStub(channel)

    print("Supported languages: Python, C, Java, JavaScript")
    language = input("Enter language: ").strip().lower()

    if language not in {"python", "java", "javascript"}:
        print("Unsupported language!")
        return

    print("Enter code (leave an empty line and press Enter to finish):")

    code_lines = []
    while True:
        line = input()
        if line == "":  # Stop when an empty line is entered
            break
        code_lines.append(line)

    code = "\n".join(code_lines)
    api_key = "secure123"  # Authentication Key
    request = code_execution_pb2.CodeRequest(language=language, code=code, api_key=api_key)

    print("\nExecuting...\n")
    response_stream = stub.ExecuteCode(request)

    for response in response_stream:
        print(response.output, end="")

if __name__ == "__main__":
    run()
