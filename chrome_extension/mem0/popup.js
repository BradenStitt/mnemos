document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const memoriesContainer = document.getElementById('memoriesContainer');
  
  let isSearching = false;

  // Check if service is available
  async function checkServiceStatus() {
    try {
      const response = await fetch('http://localhost:8000/api/test', { 
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        console.log('Memory service is running');
        return true;
      } else {
        console.log('Memory service responded but with error');
        return false;
      }
    } catch (error) {
      console.error('Memory service is not available:', error);
      showError('Memory service is not available. Please make sure it\'s running on localhost:8000');
      return false;
    }
  }

  // Search memories
  async function searchMemories(query) {
    if (!query.trim()) {
      showEmptyState('Please enter a search query');
      return;
    }

    setLoading(true);
    
    try {
      // Try cascading retrieval first (combines dense and sparse search)
      let response = await fetch(`http://localhost:8000/api/cascading-retrieval?text_query=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      let data = await response.json();
      
      console.log('Cascading API Response:', data); // Debug log
      
      // If no results from cascading, try semantic search as fallback
      if (!data.results || data.results.length === 0) {
        console.log('No results from cascading, trying semantic search...');
        response = await fetch(`http://localhost:8000/api/semantic-search?text_query=${encodeURIComponent(query)}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        data = await response.json();
        console.log('Semantic API Response:', data); // Debug log
      }
      
      if (data.results && data.results.length > 0) {
        displayMemories(data.results);
      } else {
        showEmptyState('No memories found for your search');
      }
    } catch (error) {
      console.error('Error searching memories:', error);
      console.error('Error details:', error.message);
      showError(`Failed to search memories: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  // Display memories in the container
  function displayMemories(memories) {
    memoriesContainer.innerHTML = '';
    
    memories.forEach((memory, index) => {
      const memoryElement = document.createElement('div');
      memoryElement.className = 'memory-item';
      memoryElement.innerHTML = `
        <div class="memory-text">${escapeHtml(memory.chunk_text || memory.text || 'No text available')}</div>
        <div class="memory-meta">
          <span>Score: ${(memory.score * 100).toFixed(1)}%</span>
          <span>Memory #${index + 1}</span>
        </div>
      `;
      
      // Add click handler to copy memory to clipboard
      memoryElement.addEventListener('click', () => {
        const text = memory.chunk_text || memory.text || '';
        navigator.clipboard.writeText(text).then(() => {
          // Show a brief success indicator
          memoryElement.style.backgroundColor = '#34a853';
          setTimeout(() => {
            memoryElement.style.backgroundColor = '';
          }, 500);
        }).catch(err => {
          console.error('Failed to copy text: ', err);
        });
      });
      
      memoriesContainer.appendChild(memoryElement);
    });
  }

  // Show loading state
  function setLoading(loading) {
    isSearching = loading;
    searchButton.disabled = loading;
    searchButton.textContent = loading ? 'Searching...' : 'Search Memories';
    
    if (loading) {
      memoriesContainer.innerHTML = '<div class="loading">Searching your memories...</div>';
    }
  }

  // Show error state
  function showError(message) {
    memoriesContainer.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
  }

  // Show empty state
  function showEmptyState(message) {
    memoriesContainer.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Event listeners
  searchButton.addEventListener('click', () => {
    if (!isSearching) {
      searchMemories(searchInput.value);
    }
  });

  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isSearching) {
      searchMemories(searchInput.value);
    }
  });

  // Check service status when popup opens
  checkServiceStatus();
});