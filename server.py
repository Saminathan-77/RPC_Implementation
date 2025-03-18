import grpc
import subprocess
import code_execution_pb2
import code_execution_pb2_grpc
from concurrent import futures
import os

# Directory for storing temporary files
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

VALID_API_KEYS = {"secure123"}  # API Key-based Authentication

class CodeExecutionServicer(code_execution_pb2_grpc.CodeExecutionServiceServicer):
    def ExecuteCodeBatch(self, request, context):
        responses = []
        
        for req in request.requests:
            if req.api_key not in VALID_API_KEYS:
                responses.append(code_execution_pb2.ExecutionResponse(output="Unauthorized Access"))
                continue

            language = req.language.lower()
            code = req.code
            output = self.execute_code(language, code)
            responses.append(code_execution_pb2.ExecutionResponse(output=output))
        
        return code_execution_pb2.CodeBatchResponse(responses=responses)

    def execute_code(self, language, code):
        """Executes code based on language and returns output"""
        try:
            if language == "python":
                command = ["python", "-c", code]

            elif language == "java":
                file_path = os.path.join(FILES_DIR, "Main.java")

                with open(file_path, "w") as f:
                    f.write(code)
                
                compile_result = subprocess.run(["javac", file_path], capture_output=True, text=True)
                if compile_result.returncode != 0:
                    return compile_result.stderr

                command = ["java", "-cp", FILES_DIR, "Main"]

            elif language == "javascript":
                file_path = os.path.join(FILES_DIR, "temp.js")

                with open(file_path, "w") as f:
                    f.write(code)

                command = ["node", file_path]

            else:
                return "Unsupported Language"

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(timeout=5)
            return stdout + stderr

        except subprocess.TimeoutExpired:
            return "Execution Timed Out"
        except Exception as e:
            return str(e)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    code_execution_pb2_grpc.add_CodeExecutionServiceServicer_to_server(CodeExecutionServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("Server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
