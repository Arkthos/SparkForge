"""Synthetic-only checks; never read exported wiki source files."""

import html
import unittest

from . import collect_wiki as collector


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            "wiki_id": "00000000-0000-0000-0000-000000000001", "wiki_name": "ExampleProject.wiki",
            "project_id": "00000000-0000-0000-0000-000000000002", "project_name": "ExampleProject",
            "repository_id": "00000000-0000-0000-0000-000000000003",
            "service_urls": [
                "https://example-org.visualstudio.com/ExampleProject",
                "https://dev.azure.com/example-org/ExampleProject",
            ],
            "commit": "a" * 40, "branch": "wikiBranch", "root_path": "/AI",
        }
        self.page = {"key": "root", "path": "/AI", "git_path": "/AI.md", "page_id": 1}
        self.child = {"key": "child", "path": "/AI/Child", "git_path": "/AI/Child.md", "page_id": 2}
        self.pages = [self.page, self.child]

    def classify(self, target, page=None):
        return collector.classify_reference(target, page or self.page, self.snapshot, self.pages, {})

    def test_root_attachment(self):
        result = self.classify("/.attachments/image%20one.png")
        self.assertEqual(result["kind"], "WIKI_ATTACHMENT")
        self.assertEqual(result["git_path"], "/.attachments/image one.png")

    def test_relative_attachment(self):
        self.assertEqual(self.classify("../.attachments/image.png", self.child)["git_path"], "/.attachments/image.png")

    def test_same_wiki_page_id(self):
        result = self.classify("https://example-org.visualstudio.com/ExampleProject/_wiki/wikis/ExampleProject.wiki/2/Child")
        self.assertEqual(result["page_key"], "child")

    def test_dev_azure_alias(self):
        result = self.classify("https://dev.azure.com/example-org/ExampleProject/_wiki/wikis/ExampleProject.wiki/2/Child")
        self.assertEqual(result["page_key"], "child")

    def test_other_project_not_followed(self):
        result = self.classify("https://example-org.visualstudio.com/Other/_wiki/wikis/ExampleProject.wiki/2/Child")
        self.assertEqual(result["kind"], "OTHER_PROJECT_REFERENCE")

    def test_external_host_not_followed(self):
        self.assertEqual(self.classify("https://example.test/.attachments/image.png")["kind"], "EXTERNAL_REFERENCE")

    def test_relative_page_and_outside_scope(self):
        self.assertEqual(self.classify("/AI/Child")["kind"], "IN_SCOPE_PAGE")
        self.assertEqual(self.classify("/Unrelated")["kind"], "OUT_OF_SCOPE_WIKI_PAGE")
        self.assertFalse(collector.in_scope("/AIX/Other", "/AI"))

    def test_encoded_hyphen_alias(self):
        self.child["git_path"], self.child["path"] = "/AI/A%2DB.md", "/AI/A-B"
        self.assertEqual(self.classify("/AI/A%2DB")["page_key"], "child")

    def test_bare_url_markdown_emphasis_is_deduplicated(self):
        target = "https://example.test/page"
        references, _ = collector.extract_references("**[label](" + target + ")**", collector.markdown_parser())
        self.assertEqual([reference["target"] for reference in references], [target])

    def test_schemeless_shortlink_is_not_a_wiki_child(self):
        self.assertEqual(self.classify("aka.ms/example")["kind"], "EXTERNAL_REFERENCE")

    def test_other_revision_not_followed(self):
        result = self.classify("/.attachments/image.png?versionDescriptor.version=" + "b" * 40)
        self.assertEqual(result["kind"], "CROSS_VERSION_ATTACHMENT_REFERENCE")

    def test_no_active_uri_fetch(self):
        self.assertEqual(self.classify("javascript:alert(1)")["kind"], "UNSUPPORTED_URI_SCHEME")
        self.assertEqual(self.classify("file:///C:/sensitive.txt")["kind"], "UNSUPPORTED_URI_SCHEME")

    def test_standard_markdown_and_html(self):
        source = (
            "![image](/.attachments/a%20b.png)\n[document][reference]\n\n"
            "[reference]: /.attachments/document.pdf\n\n"
            '<img src="/.attachments/inline.png">\n\n[child](/AI/Child)\n'
        )
        references, unresolved = collector.extract_references(source, collector.markdown_parser())
        self.assertEqual({ref["target"] for ref in references}, {
            "/.attachments/a%20b.png", "/.attachments/document.pdf", "/.attachments/inline.png", "/AI/Child",
        })
        self.assertEqual(unresolved, [])

    def test_parentheses_and_resize(self):
        source = "![image](/.attachments/a(b).png)\n![image](/.attachments/resized.png =400x200)\n"
        references, unresolved = collector.extract_references(source, collector.markdown_parser())
        self.assertEqual({ref["target"] for ref in references}, {"/.attachments/a(b).png", "/.attachments/resized.png"})
        self.assertEqual(unresolved, [])

    def test_unparsed_marker_is_not_silently_complete(self):
        references, unresolved = collector.extract_references("Custom attachment: .attachments/odd.png\n", collector.markdown_parser())
        self.assertEqual(references, [])
        self.assertEqual(len(unresolved), 1)

    def test_code_not_an_instruction_or_attachment_link(self):
        references, unresolved = collector.extract_references("```text\n[not a link](/.attachments/code.png)\n```\n", collector.markdown_parser())
        self.assertEqual(references, [])
        self.assertEqual(unresolved, [])

    def test_escaped_view_cannot_execute_source_markup(self):
        source = '<script>alert("untrusted")</script><img src="https://example.test/x">'
        document = collector.html_document("Synthetic", "<pre>" + html.escape(source) + "</pre>")
        self.assertNotIn("<script>", document)
        self.assertNotIn('<img src="https://', document)
        self.assertIn("default-src 'none'", document)
        parser = collector.HtmlReferences()
        parser.feed(document)
        self.assertEqual(parser.targets, [])


if __name__ == "__main__":
    unittest.main()
