import grpc
import code_execution_pb2
import code_execution_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = code_execution_pb2_grpc.CodeExecutionServiceStub(channel)

    print("Supported languages: Python, Java, JavaScript")

    requests = []
    api_key = "secure123" 

    while True:
        language = input("Enter language (or 'done' to execute batch): ").strip().lower()
        if language == "done":
            break

        if language not in {"python", "java", "javascript"}:
            print("Unsupported language!")
            continue

        print("Enter code (leave an empty line and press Enter to finish):")
        code_lines = []
        while True:
            line = input()
            if line == "":
                break
            code_lines.append(line)

        code = "\n".join(code_lines)
        requests.append(code_execution_pb2.CodeRequest(language=language, code=code, api_key=api_key))

    if not requests:
        print("No code entered. Exiting...")
        return

    print("\nExecuting batch...\n")
    batch_request = code_execution_pb2.CodeBatchRequest(requests=requests)
    response = stub.ExecuteCodeBatch(batch_request)

    print("\nResults:\n")
    for idx, res in enumerate(response.responses):
        print(f"Code {idx + 1} Output:\n{res.output}\n{'-' * 40}")

if __name__ == "__main__":
    run()
