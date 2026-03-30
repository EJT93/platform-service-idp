FROM public.ecr.aws/lambda/python:3.12

COPY src/ ${LAMBDA_TASK_ROOT}/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["handlers.service_handler.handler"]
