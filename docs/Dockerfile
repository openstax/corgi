FROM sphinxdoc/sphinx:7.1.2 as base

COPY requirements.txt /docs/requirements.txt
RUN pip install watchdog && pip install -r /docs/requirements.txt


FROM base as runner

COPY . /docs
EXPOSE 8000

COPY <<EOT /entrypoint.bash
  repo_root=/corgi
  script="\$repo_root/scripts/generate-docs.py"
  readme_file="\$repo_root/README.md"
  output_dir="/docs/auto/readme"
  build_command="python \$script \$repo_root \$readme_file \$output_dir"
  \$build_command
  watchmedo shell-command --pattern=README.md --command="\$build_command" --drop "\$repo_root" &
  sphinx-autobuild --host 0.0.0.0 --port 8000 /docs /build/html
EOT

CMD bash -ex /entrypoint.bash
