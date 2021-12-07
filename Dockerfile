FROM python:3.8.12

# upgrade pip
RUN pip install -U --upgrade pip

WORKDIR /workspace

# install requirements
RUN pip install --no-cache-dir \
	dvc==2.8.3 \
	flask==2.0.2 \
	pandas==1.3.4 \
	scikit-learn==1.0.1
EXPOSE 8889

ENTRYPOINT [""]
CMD [""]