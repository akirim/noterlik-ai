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
        // Simüle edilmiş veri - gerçek implementasyonda JSON dosyalarından yüklenecek
        this.data = [
            {
                title: "1990-18 sayılı genelge",
                description: "Nüfus cüzdanı, pasaport ve benzeri işlemlerin tasdikli suretlerini her sayfasından ayrı ayrı tarifede yer alan harç miktarının tahsili icap eder.",
                category: "genelge",
                year: "1990",
                file: "1990-18-sayili-genelge.html",
                keywords: ["nüfus cüzdanı", "pasaport", "harç", "tasdikli suret"]
            },
            {
                title: "132 sayılı kanun",
                description: "TÜRK STANDARDLARI ENSTİTÜSÜ KURULUŞ KANUNU - Kanun Numarası : 132 Kabul Tarihi : 18/11/1960",
                category: "kanun",
                year: "1960",
                file: "132-sayili-kanun.html",
                keywords: ["tse", "standart", "kuruluş", "kanun"]
            },
            {
                title: "Vekaletname düzeltme beyannamesi",
                description: "Vekaletname düzeltme işlemleri hakkında mahkeme kararları ve uygulama esasları.",
                category: "mahkeme",
                year: "2023",
                file: "vekaletname-duzeltme-beyannamesi.html",
                keywords: ["vekaletname", "düzeltme", "beyanname", "mahkeme"]
            },
            {
                title: "Finansal kiralama sözleşmesi yazısı",
                description: "Finansal kiralama sözleşmelerinin noterlik işlemleri ve hukuki düzenlemeleri.",
                category: "sozlesme",
                year: "2022",
                file: "finansal-kiralama-sozlesmesi-yazisi.html",
                keywords: ["finansal kiralama", "sözleşme", "kira", "noterlik"]
            },
            {
                title: "Noterin hukuki sorumluluğu",
                description: "Noterlerin hukuki sorumlulukları hakkında mahkeme kararları ve yasal düzenlemeler.",
                category: "noterlik",
                year: "2023",
                file: "noterin-hukuki-sorumlulugu-hak-mahkeme-kararlari.html",
                keywords: ["noter", "sorumluluk", "hukuki", "mahkeme kararı"]
            },
            {
                title: "Avukat dışındakiler için dava vekaletnamesi",
                description: "Avukat olmayan kişiler için dava vekaletnamesi düzenlenmesi ve şartları.",
                category: "vekalet",
                year: "2021",
                file: "avukat-disindakiler-icin-dava-vekaletnamesi.html",
                keywords: ["avukat", "vekaletname", "dava", "temsil"]
            }
        ];

        // Daha fazla simüle edilmiş veri ekle
        for (let i = 0; i < 100; i++) {
            const years = ['1970', '1980', '1990', '2000', '2010', '2020', '2023'];
            const categories = ['genelge', 'kanun', 'mahkeme', 'sozlesme', 'vekalet', 'noterlik'];
            const categoryNames = {
                'genelge': 'Genelge',
                'kanun': 'Kanun',
                'mahkeme': 'Mahkeme Kararı',
                'sozlesme': 'Sözleşme',
                'vekalet': 'Vekaletname',
                'noterlik': 'Noterlik İşlemi'
            };

            const category = categories[Math.floor(Math.random() * categories.length)];
            const year = years[Math.floor(Math.random() * years.length)];
            
            this.data.push({
                title: `${year}-${Math.floor(Math.random() * 100)} sayılı ${categoryNames[category].toLowerCase()}`,
                description: `${categoryNames[category]} hakkında detaylı bilgiler ve yasal düzenlemeler.`,
                category: category,
                year: year,
                file: `${year}-${Math.floor(Math.random() * 100)}-sayili-${category}.html`,
                keywords: [category, year, "hukuk", "yasal"]
            });
        }

        this.filteredData = [...this.data];
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
