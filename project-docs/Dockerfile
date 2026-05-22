FROM squidfunk/mkdocs-material:9

WORKDIR /docs
COPY mkdocs.yml ./
COPY docs ./docs

# Проверяем сборку на этапе image build
RUN mkdocs build -q

EXPOSE 8000
CMD ["serve", "-a", "0.0.0.0:8000", "--no-livereload"]
