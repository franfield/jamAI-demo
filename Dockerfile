FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies including C++ compiler and development tools
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y wget tar gzip gcc gcc-c++ make automake autoconf libtool \
    libpng-devel libjpeg-devel libtiff-devel zlib-devel libwebp-devel \
    libtool-ltdl-devel pkg-config

# Install Leptonica (dependency for Tesseract)
WORKDIR /tmp
RUN wget https://github.com/DanBloomberg/leptonica/releases/download/1.82.0/leptonica-1.82.0.tar.gz && \
    tar -xzvf leptonica-1.82.0.tar.gz && \
    cd leptonica-1.82.0 && \
    ./configure --prefix=/usr && \
    make && \
    make install

# Make sure pkg-config can find leptonica
ENV PKG_CONFIG_PATH=/usr/lib/pkgconfig:$PKG_CONFIG_PATH

# Install Tesseract OCR
WORKDIR /tmp
RUN wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.3.0.tar.gz && \
    tar -xzvf 5.3.0.tar.gz && \
    cd tesseract-5.3.0 && \
    ./autogen.sh && \
    PKG_CONFIG_PATH=/usr/lib/pkgconfig ./configure --prefix=/usr && \
    make && \
    make install

# Install language data (you can add more languages as needed)
WORKDIR /tmp
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    mkdir -p /usr/share/tessdata/ && \
    mv eng.traineddata /usr/share/tessdata/

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tessdata/
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy function code
COPY app ${LAMBDA_TASK_ROOT}/app

# Debug: List files in LAMBDA_TASK_ROOT to verify what was copied
RUN ls -la ${LAMBDA_TASK_ROOT}
# Debug: Print Python path
RUN python -c "import sys; print(sys.path)"

# Set the CMD to your handler
CMD [ "app.handler.lambda_handler" ]