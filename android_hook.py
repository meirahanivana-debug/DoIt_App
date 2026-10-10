from pathlib import Path
from xml.etree import ElementTree


ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"
ANDROID_NAME = f"{{{ANDROID_NAMESPACE}}}name"


def before_apk_build(toolchain):
    manifest_path = Path.cwd() / "src" / "main" / "AndroidManifest.xml"
    tree = ElementTree.parse(manifest_path)
    root = tree.getroot()

    applications = root.findall("application")
    if not applications:
        raise RuntimeError(f"No application element found in {manifest_path}")

    primary_application = applications[0]
    existing_receivers = {
        child.get(ANDROID_NAME)
        for child in primary_application.findall("receiver")
    }

    # Buildozer injects extra manifest XML as a literal application block string
    # containing receiver entries and may also leave other child tags such as
    # meta-data in the extra block. Only keep supported receiver nodes and discard
    # the rest to avoid invalid manifest structure.
    for extra_application in applications[1:]:
        for child in list(extra_application):
            if child.tag == "receiver":
                name = child.get(ANDROID_NAME)
                if name and name not in existing_receivers:
                    primary_application.append(child)
                    existing_receivers.add(name)
        root.remove(extra_application)

    expected_receivers = {
        "org.doit.doitapp.DeadlineReminderReceiver",
        "org.doit.doitapp.DeadlineBootReceiver",
    }
    if not expected_receivers.issubset(existing_receivers):
        raise RuntimeError("Deadline reminder receivers are missing from the manifest")

    ElementTree.register_namespace("android", ANDROID_NAMESPACE)
    tree.write(manifest_path, encoding="utf-8", xml_declaration=True)
