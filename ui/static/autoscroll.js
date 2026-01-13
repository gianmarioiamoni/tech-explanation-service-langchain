// Autoscroll functionality for Gradio output textbox
// This script runs after Gradio components are rendered

console.log('🧪 AUTOSCROLL: External script loaded');

function setupAutoscroll() {
    console.log('🔍 AUTOSCROLL: Searching for explanation textarea...');
    
    // Find all textareas
    const allTextareas = document.querySelectorAll('textarea');
    console.log('📊 AUTOSCROLL: Found', allTextareas.length, 'textareas');
    
    allTextareas.forEach((textarea, index) => {
        // Try to find the label by going up the DOM tree
        const container = textarea.closest('[class*="textbox"]') || textarea.closest('label');
        const labelText = container?.textContent || 'No label';
        
        console.log(`   Textarea ${index}: ${labelText.substring(0, 50)}`);
        
        // Find the explanation textarea by its label containing "Explanation" or "💡"
        if (labelText.includes('Explanation') || labelText.includes('💡')) {
            console.log('   ✅ FOUND explanation textarea!');
            console.log('   📐 Initial ScrollHeight:', textarea.scrollHeight);
            
            // Setup aggressive autoscroll with polling
            let lastScrollHeight = textarea.scrollHeight;
            
            const scrollInterval = setInterval(() => {
                if (textarea.scrollHeight !== lastScrollHeight) {
                    textarea.scrollTop = textarea.scrollHeight;
                    lastScrollHeight = textarea.scrollHeight;
                    console.log('   📜 Scrolled to bottom (new height:', textarea.scrollHeight, ')');
                }
            }, 100); // Poll every 100ms
            
            // Also setup MutationObserver as backup
            const observer = new MutationObserver(() => {
                textarea.scrollTop = textarea.scrollHeight;
            });
            
            observer.observe(textarea, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true
            });
            
            console.log('   ✅ AUTOSCROLL ACTIVE (polling + observer)');
            return true;
        }
    });
    
    return false;
}

// Try immediately
setTimeout(() => {
    console.log('⏰ AUTOSCROLL: First attempt after 1s...');
    if (!setupAutoscroll()) {
        console.log('⚠️ AUTOSCROLL: Textarea not found, retrying in 2s...');
        // Retry after 2 more seconds if not found
        setTimeout(() => {
            console.log('⏰ AUTOSCROLL: Second attempt after 3s...');
            if (!setupAutoscroll()) {
                console.log('❌ AUTOSCROLL: Failed to find explanation textarea');
            }
        }, 2000);
    }
}, 1000);

