FROM python:3.13-slim-bookworm

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium + all system-level dependencies it needs.
# PLAYWRIGHT_BROWSERS_PATH must be a fixed system path (not /root/) so the
# browser is accessible when Apptainer runs the container as the host user.
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
RUN playwright install chromium --with-deps \
    && chmod -R 755 /opt/playwright-browsers

# Copy source code
COPY models/ ./models/
COPY *.py ./

# Pre-generate the 30 layout templates so they are baked into the image
# and do not need to be re-generated on every container start.
RUN python template_generator.py

ENV PYTHONUNBUFFERED=1

# No fixed entrypoint — the caller specifies which script to run.
# Output always goes to a mounted host volume via -o:
#
#   docker run --rm -v /host/data:/data <image> python generate.py -n 500 -o /data
#   docker run --rm -v /host/data:/data <image> python annotate.py -o /data
#   docker run --rm -v /host/data:/data <image> python visualize_annotations.py -o /data
#
# Apptainer (cluster):
#   apptainer build data_gen.sif docker-daemon://data-gen:latest
#   apptainer run --bind /host/data:/data data_gen.sif python generate.py -n 500 -o /data
