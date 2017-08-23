If Windows Vista API is used for eventlogs then eventlogs with spaces are not recognized correctly.

diff --git a/agents/windows/sections/SectionEventlog.h b/agents/windows/sections/SectionEventlog.h
index 214f72d53c..70de4dcf30 100644
--- a/agents/windows/sections/SectionEventlog.h
+++ b/agents/windows/sections/SectionEventlog.h
@@ -51,5 +51,5 @@ public:
         std::string key;
         getline(str, key, ' ');
-        getline(str, entry.name, ' ');
+        getline(str, entry.name, '=');
         entry.vista_api = (key == "logname");
         add(entry);
