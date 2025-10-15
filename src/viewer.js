/**
 * Noterlik Veri Görüntüleyici
 * Basit ve işlevsel veri görüntüleme arayüzü
 */

class NoterlikViewer {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.currentCategory = 'all';
        this.searchTerm = '';
        
        this.initializeElements();
        this.bindEvents();
        this.loadData();
    }

    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.resultsList = document.getElementById('resultsList');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.noResults = document.getElementById('noResults');
        this.categoryBtns = document.querySelectorAll('.category-btn');
    }

    bindEvents() {
        // Arama
        this.searchInput.addEventListener('input', () => this.handleSearch());
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });

        // Kategori filtreleri
        this.categoryBtns.forEach(btn => {
            btn.addEventListener('click', () => this.handleCategoryFilter(btn));
        });
    }

    async loadData() {
        try {
            // Simüle edilmiş veri yükleme
            this.showLoading();
            
            // Gerçek implementasyonda JSON dosyalarını yükleyecek
            await this.loadMockData();
            
            this.hideLoading();
            this.displayResults();
            
        } catch (error) {
            console.error('Veri yükleme hatası:', error);
            this.showError('Veriler yüklenirken bir hata oluştu.');
        }
    }

    async loadMockData() {
        try {
            // Gerçek JSON dosyalarını yükle
            const response = await fetch('json_output/master_index.json');
            if (!response.ok) {
                throw new Error('Master index dosyası bulunamadı');
            }
            
            const masterIndex = await response.json();
            
            if (masterIndex.total_files === 0 || !masterIndex.files || masterIndex.files.length === 0) {
                console.warn('Master index boş, örnek dosyalardan veri yükleniyor...');
                await this.loadSampleData();
                return;
            }

            // Master index'ten verileri yükle
            this.data = masterIndex.files.map(file => {
                const category = this.categorizeFile(file.file_path);
                const year = this.extractYear(file.file_path);
                
                return {
                    title: file.title || this.extractTitleFromPath(file.file_path),
                    description: file.description || 'Detaylı bilgi için dosyayı açın.',
                    category: category,
                    year: year,
                    file: file.file_path.replace(/\\/g, '/').replace('.json', '.html'),
                    keywords: file.keywords || [],
                    wordCount: file.word_count || 0,
                    linkCount: file.link_count || 0,
                    imageCount: file.image_count || 0
                };
            });

            console.log(`${this.data.length} gerçek dosya yüklendi`);
            
        } catch (error) {
            console.error('Gerçek veri yükleme hatası:', error);
            console.log('Örnek veriler yükleniyor...');
            await this.loadSampleData();
        }

        this.filteredData = [...this.data];
        this.updateStats();
    }

    updateStats() {
        if (this.data.length === 0) return;

        // Kategori istatistikleri
        const categoryStats = {};
        const years = new Set();
        let totalWords = 0;

        this.data.forEach(item => {
            categoryStats[item.category] = (categoryStats[item.category] || 0) + 1;
            if (item.year) years.add(item.year);
            if (item.wordCount) totalWords += item.wordCount;
        });

        // DOM güncellemeleri
        const totalDocsEl = document.getElementById('totalDocs');
        const totalGenelgesEl = document.getElementById('totalGenelges');
        const totalKanunlarEl = document.getElementById('totalKanuns');
        const totalMahkemeEl = document.getElementById('totalKarars');

        if (totalDocsEl) totalDocsEl.textContent = this.data.length.toLocaleString('tr-TR');
        if (totalGenelgesEl) totalGenelgesEl.textContent = (categoryStats.genelge || 0).toLocaleString('tr-TR');
        if (totalKanunlarEl) totalKanunlarEl.textContent = (categoryStats.kanun || 0).toLocaleString('tr-TR');
        if (totalMahkemeEl) totalMahkemeEl.textContent = (categoryStats.mahkeme || 0).toLocaleString('tr-TR');

        console.log('İstatistikler güncellendi:', {
            totalDocs: this.data.length,
            categories: categoryStats,
            yearRange: years.size > 0 ? `${Math.min(...years)}-${Math.max(...years)}` : '2023',
            totalWords: totalWords
        });
    }

    async loadSampleData() {
        // Örnek JSON dosyalarından veri yükle
        const sampleFiles = [
            '1990-18-sayili-genelge.json',
            '132-sayili-kanun.json',
            'vekaletname-duzeltme-beyannamesi.json',
            'finansal-kiralama-sozlesmesi-yazisi.json',
            'noterin-hukuki-sorumlulugu-hak-mahkeme-kararlari.json',
            'avukat-disindakiler-icin-dava-vekaletnamesi.json'
        ];

        this.data = [];

        for (const fileName of sampleFiles) {
            try {
                const response = await fetch(`json_output/A7614095-C9D7-4C82-8BBC-8DB7279DFB60/${fileName}`);
                if (response.ok) {
                    const jsonData = await response.json();
                    const category = this.categorizeFile(fileName);
                    const year = this.extractYear(fileName);
                    
                    this.data.push({
                        title: jsonData.metadata.title || this.extractTitleFromPath(fileName),
                        description: jsonData.metadata.description || jsonData.content.text.substring(0, 200) + '...',
                        category: category,
                        year: year,
                        file: fileName.replace('.json', '.html'),
                        keywords: jsonData.metadata.keywords || [],
                        wordCount: jsonData.content.text.split(' ').length,
                        linkCount: jsonData.content.links.length,
                        imageCount: jsonData.content.images.length
                    });
                }
            } catch (error) {
                console.warn(`Örnek dosya yüklenemedi: ${fileName}`, error);
            }
        }

        console.log(`${this.data.length} örnek dosya yüklendi`);
    }

    categorizeFile(filePath) {
        const fileName = filePath.toLowerCase();
        
        if (fileName.includes('genelge') || /\d{4}-\d+-sayili-genelge/.test(fileName)) {
            return 'genelge';
        } else if (fileName.includes('kanun') || fileName.includes('law')) {
            return 'kanun';
        } else if (fileName.includes('mahkeme') || fileName.includes('karar')) {
            return 'mahkeme';
        } else if (fileName.includes('sozlesme') || fileName.includes('sözleşme')) {
            return 'sozlesme';
        } else if (fileName.includes('vekalet') || fileName.includes('vekaletname')) {
            return 'vekalet';
        } else if (fileName.includes('noterlik') || fileName.includes('noter')) {
            return 'noterlik';
        }
        
        return 'diger';
    }

    extractYear(filePath) {
        const match = filePath.match(/(\d{4})/);
        return match ? match[1] : '2023';
    }

    extractTitleFromPath(filePath) {
        const fileName = filePath.split('/').pop().split('.')[0];
        return fileName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    handleSearch() {
        this.searchTerm = this.searchInput.value.toLowerCase().trim();
        this.applyFilters();
    }

    handleCategoryFilter(btn) {
        // Aktif kategori butonunu güncelle
        this.categoryBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        this.currentCategory = btn.dataset.category;
        this.applyFilters();
    }

    applyFilters() {
        this.filteredData = this.data.filter(item => {
            // Kategori filtresi
            const categoryMatch = this.currentCategory === 'all' || item.category === this.currentCategory;
            
            // Arama filtresi
            const searchMatch = !this.searchTerm || 
                item.title.toLowerCase().includes(this.searchTerm) ||
                item.description.toLowerCase().includes(this.searchTerm) ||
                item.keywords.some(keyword => keyword.toLowerCase().includes(this.searchTerm)) ||
                item.year.includes(this.searchTerm);
            
            return categoryMatch && searchMatch;
        });

        this.displayResults();
    }

    displayResults() {
        if (this.filteredData.length === 0) {
            this.showNoResults();
            return;
        }

        this.resultsList.innerHTML = '';
        
        this.filteredData.slice(0, 50).forEach(item => {
            const resultElement = this.createResultElement(item);
            this.resultsList.appendChild(resultElement);
        });

        this.showResults();
    }

    createResultElement(item) {
        const div = document.createElement('div');
        div.className = 'result-item';
        
        const categoryBadges = {
            'genelge': 'Genelge',
            'kanun': 'Kanun',
            'mahkeme': 'Mahkeme Kararı',
            'sozlesme': 'Sözleşme',
            'vekalet': 'Vekaletname',
            'noterlik': 'Noterlik'
        };

        div.innerHTML = `
            <div class="result-title">${item.title}</div>
            <div class="result-meta">
                <span class="category-badge">${categoryBadges[item.category]}</span>
                <span><i class="fas fa-calendar me-1"></i>${item.year}</span>
                <span class="ms-3"><i class="fas fa-file me-1"></i>${item.file}</span>
            </div>
            <div class="result-description">${item.description}</div>
        `;

        div.addEventListener('click', () => this.openDocument(item));
        
        return div;
    }

    openDocument(item) {
        // Gerçek implementasyonda dosyayı açacak
        alert(`Doküman açılıyor: ${item.title}\nDosya: ${item.file}`);
        
        // Gerçek implementasyon:
        // window.open(`db/A7614095-C9D7-4C82-8BBC-8DB7279DFB60/${item.file}`, '_blank');
    }

    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.resultsList.style.display = 'none';
        this.noResults.style.display = 'none';
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }

    showResults() {
        this.resultsList.style.display = 'block';
        this.noResults.style.display = 'none';
    }

    showNoResults() {
        this.resultsList.style.display = 'none';
        this.noResults.style.display = 'block';
    }

    showError(message) {
        this.hideLoading();
        this.resultsList.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
        this.showResults();
    }

    // Utility methods
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR');
    }
}

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    window.noterlikViewer = new NoterlikViewer();
});

// Sayfa kapatılırken temizlik
window.addEventListener('beforeunload', () => {
    if (window.noterlikViewer) {
        // Gerekli temizlik işlemleri
    }
});
