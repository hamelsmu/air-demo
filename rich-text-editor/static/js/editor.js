/**
 * TipTap Editor Module for Air Demo
 * Demonstrates clean separation of editor logic from templates
 * 
 * This module uses HTMX integration pattern:
 * - No hidden input field for content
 * - Content is injected via htmx:configRequest event
 * - Editor instance is stored on form._editor for access during submission
 */

import { Editor } from 'https://esm.sh/@tiptap/core@2.10.3';
import StarterKit from 'https://esm.sh/@tiptap/starter-kit@2.10.3';
import Underline from 'https://esm.sh/@tiptap/extension-underline@2.10.3';
import Link from 'https://esm.sh/@tiptap/extension-link@2.10.3';

/**
 * Initialize a TipTap editor instance
 * @param {HTMLElement} container - The container element with [data-tiptap] attribute
 * @param {string|null} initialHTML - Initial HTML content for the editor
 */
window.initEditor = function(container, initialHTML) {
    const form = container.closest('form');
    
    const editor = new Editor({
        element: container,
        extensions: [
            StarterKit,
            Underline,
            Link.configure({
                openOnClick: false,
                HTMLAttributes: {
                    class: 'text-primary hover:underline',
                }
            })
        ],
        content: initialHTML || '',
        editorProps: { 
            attributes: { 
                class: 'tiptap'
            }
        },
        onUpdate: () => {
            const btn = document.getElementById('save-btn');
            if (btn && btn.classList.contains('saved')) {
                btn.textContent = 'Save';
                btn.classList.remove('saved');
            }
        }
    });
    
    if (form) form._editor = editor;
    
    const toolbar = container.parentElement.querySelector('.button-group');
    if (toolbar) {
        toolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            if (btn && !btn.disabled) {
                handleToolbarAction(editor, btn.dataset.action);
            }
        });
        
        editor.on('update', () => updateToolbarState(editor, toolbar));
        editor.on('selectionUpdate', () => updateToolbarState(editor, toolbar));
        updateToolbarState(editor, toolbar);
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts(editor, form);
};

/**
 * Handle toolbar button actions
 * @param {Editor} editor - TipTap editor instance
 * @param {string} action - Action name from data-action attribute
 */
function handleToolbarAction(editor, action) {
    const chain = editor.chain().focus();
    
    switch (action) {
        case 'bold':
        case 'italic':
        case 'underline':
        case 'strike':
        case 'code':
        case 'blockquote':
            chain[`toggle${action.charAt(0).toUpperCase() + action.slice(1)}`]().run();
            break;
        case 'h1':
            chain.toggleHeading({ level: 1 }).run();
            break;
        case 'h2':
            chain.toggleHeading({ level: 2 }).run();
            break;
        case 'h3':
            chain.toggleHeading({ level: 3 }).run();
            break;
        case 'bullet-list':
            chain.toggleBulletList().run();
            break;
        case 'ordered-list':
            chain.toggleOrderedList().run();
            break;
        case 'code-block':
            chain.toggleCodeBlock().run();
            break;
        case 'link':
            if (editor.isActive('link')) {
                chain.unsetLink().run();
            } else {
                const url = prompt('Enter URL:');
                if (url) {
                    chain.setLink({ href: url }).run();
                }
            }
            break;
        case 'undo':
            chain.undo().run();
            break;
        case 'redo':
            chain.redo().run();
            break;
    }
}

/**
 * Update toolbar button states based on editor state
 * @param {Editor} editor - TipTap editor instance
 * @param {HTMLElement} toolbar - Toolbar container element
 */
function updateToolbarState(editor, toolbar) {
    const activeStates = {
        bold: ['bold'],
        italic: ['italic'],
        underline: ['underline'],
        strike: ['strike'],
        code: ['code'],
        h1: ['heading', { level: 1 }],
        h2: ['heading', { level: 2 }],
        h3: ['heading', { level: 3 }],
        'bullet-list': ['bulletList'],
        'ordered-list': ['orderedList'],
        'code-block': ['codeBlock'],
        blockquote: ['blockquote'],
        link: ['link']
    };
    
    Object.entries(activeStates).forEach(([action, args]) => {
        const btn = toolbar.querySelector(`[data-action="${action}"]`);
        if (btn) btn.classList.toggle('is-active', editor.isActive(...args));
    });
    
    const undoBtn = toolbar.querySelector('[data-action="undo"]');
    const redoBtn = toolbar.querySelector('[data-action="redo"]');
    if (undoBtn) undoBtn.disabled = !editor.can().undo();
    if (redoBtn) redoBtn.disabled = !editor.can().redo();
}

/**
 * Setup keyboard shortcuts for the editor
 * @param {Editor} editor - TipTap editor instance
 * @param {HTMLFormElement} form - Form element containing the editor
 */
function setupKeyboardShortcuts(editor, form) {
    document.addEventListener('keydown', (e) => {
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const modifier = isMac ? e.metaKey : e.ctrlKey;
        
        if (modifier) {
            switch(e.key.toLowerCase()) {
                case 's':
                    e.preventDefault();
                    if (form) {
                        form.requestSubmit();
                    }
                    break;
                case 'b':
                    e.preventDefault();
                    editor.chain().focus().toggleBold().run();
                    break;
                case 'i':
                    e.preventDefault();
                    editor.chain().focus().toggleItalic().run();
                    break;
                case 'k':
                    e.preventDefault();
                    if (editor.isActive('link')) {
                        editor.chain().focus().unsetLink().run();
                    } else {
                        const url = prompt('Enter URL:');
                        if (url) {
                            editor.chain().focus().setLink({ href: url }).run();
                        }
                    }
                    break;
            }
        }
    });
}

/**
 * Initialize all TipTap editors on the page
 * This runs on page load AND after HTMX swaps new content in
 * (e.g., when you click "Load" and a new editor form is inserted)
 */
function initAllEditors() {
    document.querySelectorAll('[data-tiptap]:not([data-initialized])').forEach(container => {
        container.dataset.initialized = 'true';
        const initialHtml = container.dataset.initialHtml;
        window.initEditor(container, initialHtml ? JSON.parse(initialHtml) : null);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAllEditors);
document.body.addEventListener('htmx:afterSwap', initAllEditors);

document.body.addEventListener('htmx:configRequest', (evt) => {
    const form = evt.detail.elt;
    if (form._editor) {
        evt.detail.parameters.content = form._editor.getHTML();
    }
});

document.body.addEventListener('htmx:afterSettle', () => {
    const btn = document.getElementById('save-btn');
    if (btn && btn.classList.contains('saved')) {
        setTimeout(() => {
            const fresh = document.getElementById('save-btn');
            if (fresh && fresh.classList.contains('saved')) {
                fresh.textContent = 'Save';
                fresh.classList.remove('saved');
            }
        }, 2000);
    }
});
