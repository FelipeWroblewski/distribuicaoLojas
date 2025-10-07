 document.addEventListener("DOMContentLoaded", function() {
        
        
        var textarea = document.getElementById("create_table_sql");

        
        if (textarea) {
            
            var editor = CodeMirror.fromTextArea(textarea, {
                mode: "text/x-sql",
                theme: "monokai",   
                lineNumbers: true,  
                indentWithTabs: true,
                smartIndent: true,
                autofocus: false
            });

            var wrapper = editor.getWrapperElement();

            wrapper.classList.add(
                "border", 
                "border-gray-300", 
                "rounded-lg", 
                "shadow-md"  
            );

            var form = textarea.closest('form');
            if (form) {
                form.addEventListener('submit', function() {
                    editor.save(); 
                });
            }
        }
    });