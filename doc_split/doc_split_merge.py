import random
import fitz  # PyMuPDF

# Define document types and text file names
document_types = ["Form 1040", "Invoice", "Acord 25"]
file_name = "new.txt"

# PDF mapping
pdf_mapper = {
    "Acord 25": "acord_25.pdf",
    "Invoice": "invoice.pdf",
    "Form 1040": "form_1040.pdf"
}

# Dictionary to store page counts for each document type
page_counts = {}

# Step 1: Initialize page counts
def initialize_page_counts():
    for doc_type, pdf_path in pdf_mapper.items():
        try:
            doc = fitz.open(pdf_path)
            page_counts[doc_type] = len(doc)
            doc.close()
            print(f"[INFO] {doc_type}: {page_counts[doc_type]} pages")
        except Exception as e:
            print(f"[ERROR] Failed to open {pdf_path}: {e}")
            page_counts[doc_type] = 1  # Fallback to 1 page

# Step 2: Merge and return original list for rewriting
def get_file_merge_and_return_docs(filelist):
    output_pdf = fitz.open()
    current_page = 0
    expanded_docs = []  # To be written back to txt

    with open(filelist, "r") as file:
        doc_lines = [line.strip() for line in file.readlines()]
        print(f"[INFO] Found {len(doc_lines)} documents to merge")

    merge_log = []

    for i, doc_type in enumerate(doc_lines):
        if doc_type not in pdf_mapper:
            print(f"[WARNING] Unknown document type at position {i+1}: {doc_type}")
            continue

        pdf_path = pdf_mapper[doc_type]
        try:
            input_pdf = fitz.open(pdf_path)
            doc_page_count = len(input_pdf)
            output_pdf.insert_pdf(input_pdf)

            # Update for expanded version
            expanded_docs.extend([doc_type] * doc_page_count)

            # Log
            start_page = current_page + 1
            end_page = current_page + doc_page_count
            page_range = f"{start_page}-{end_page}" if doc_page_count > 1 else f"{start_page}"
            merge_log.append(f"Entry {i+1}: {doc_type} → PDF pages {page_range}")
            current_page += doc_page_count

            input_pdf.close()
        except Exception as e:
            print(f"[ERROR] Failed to load or insert {pdf_path} at position {i+1}: {e}")

    # Save PDF and log
    merged_output_name = filelist.replace(".txt", "_merged.pdf")
    log_file = filelist.replace(".txt", "_merge_log.txt")

    output_pdf.save(merged_output_name)
    output_pdf.close()

    with open(log_file, "w") as log:
        log.write("\n".join(merge_log))
        log.write(f"\n\nTotal pages in merged PDF: {current_page}")

    print(f"[INFO] Merged PDF saved to {merged_output_name}")
    print(f"[INFO] Merge log saved to {log_file}")
    print(f"[INFO] Total pages in merged PDF: {current_page}")

    return expanded_docs


# === RUN ===

# 1. Generate 75 random documents
random_choice_abc = [random.choice(document_types) for _ in range(75)]

# 2. Write initial choices to file (1 line per doc)
with open(file_name, "w") as file:
    file.write("\n".join(random_choice_abc))

# 3. Initialize page counts from PDFs
initialize_page_counts()

# 4. Merge + get expanded doc list
final_expanded_lines = get_file_merge_and_return_docs(file_name)

# 5. Overwrite abc.txt with expanded version (1 line per PDF page)
with open(file_name, "w") as file:
    file.write("\n".join(final_expanded_lines))

print(f"[INFO] Updated '{file_name}' to reflect actual page count ({len(final_expanded_lines)} lines)")
