/**
 * Noterlik AI - Web Scraper & JSON Converter
 * Modern ve işlevsel arayüz için JavaScript uygulaması
 */

class NoterlikApp {
    constructor() {
        this.isRunning = false;
        this.currentProcess = null;
        this.stats = {
            downloaded: 0,
            failed: 0,
            queue: 0,
            startTime: null
        };
        this.logs = [];
        
        this.initializeElements();
        this.bindEvents();
        this.initializeApp();
    }

    initializeElements() {
        // Form elements
        this.baseUrlInput = document.getElementById('baseUrl');
        this.maxConcurrentInput = document.getElementById('maxConcurrent');
        this.outputDirInput = document.getElementById('outputDir');
        
        // Buttons
        this.startScrapingBtn = document.getElementById('startScraping');
        this.convertToJsonBtn = document.getElementById('convertToJson');
        this.stopProcessBtn = document.getElementById('stopProcess');
        
        // Progress elements
        this.progressCard = document.getElementById('progressCard');
        this.progressBar = document.getElementById('progressBar');
        this.progressLabel = document.getElementById('progressLabel');
        this.progressPercent = document.getElementById('progressPercent');
        
        // Stats elements
        this.downloadedCount = document.getElementById('downloadedCount');
        this.failedCount = document.getElementById('failedCount');
        this.queueCount = document.getElementById('queueCount');
        this.elapsedTime = document.getElementById('elapsedTime');
        
        // Other elements
        this.fileTreeCard = document.getElementById('fileTreeCard');
        this.fileTree = document.getElementById('fileTree');
        this.logContainer = document.getElementById('logContainer');
    }

    bindEvents() {
        this.startScrapingBtn.addEventListener('click', () => this.startScraping());
        this.convertToJsonBtn.addEventListener('click', () => this.convertToJson());
        this.stopProcessBtn.addEventListener('click', () => this.stopProcess());
        
        // Form validation
        this.baseUrlInput.addEventListener('input', () => this.validateForm());
        this.maxConcurrentInput.addEventListener('input', () => this.validateForm());
        this.outputDirInput.addEventListener('input', () => this.validateForm());
    }

    initializeApp() {
        this.validateForm();
        this.addLog('info', 'Uygulama başlatıldı ve hazır.');
    }

    validateForm() {
        const isValid = this.baseUrlInput.value.trim() !== '' && 
                       this.maxConcurrentInput.value > 0 && 
                       this.outputDirInput.value.trim() !== '';
        
        this.startScrapingBtn.disabled = !isValid || this.isRunning;
        return isValid;
    }

    addLog(type, message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            type: type,
            message: message,
            timestamp: timestamp
        };
        
        this.logs.push(logEntry);
        
        // Log container'a ekle
        const logElement = document.createElement('div');
        logElement.className = `log-entry log-${type}`;
        logElement.innerHTML = `
            <i class="fas fa-${this.getLogIcon(type)} me-2"></i>
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;
        
        this.logContainer.appendChild(logElement);
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
        
        // Maksimum log sayısını sınırla
        if (this.logs.length > 1000) {
            this.logs.shift();
            this.logContainer.removeChild(this.logContainer.firstChild);
        }
    }

    getLogIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'info-circle';
    }

    updateProgress(percentage, label) {
        this.progressBar.style.width = `${percentage}%`;
        this.progressPercent.textContent = `${Math.round(percentage)}%`;
        this.progressLabel.textContent = label;
    }

    updateStats() {
        this.downloadedCount.textContent = this.stats.downloaded;
        this.failedCount.textContent = this.stats.failed;
        this.queueCount.textContent = this.stats.queue;
        
        if (this.stats.startTime) {
            const elapsed = Date.now() - this.stats.startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            this.elapsedTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    showProgress() {
        this.progressCard.style.display = 'block';
        this.stats.startTime = Date.now();
        
        // Stats güncelleme interval'ı başlat
        this.statsInterval = setInterval(() => {
            this.updateStats();
        }, 1000);
    }

    hideProgress() {
        this.progressCard.style.display = 'none';
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
            this.statsInterval = null;
        }
    }

    async startScraping() {
        if (!this.validateForm() || this.isRunning) return;
        
        try {
            this.isRunning = true;
            this.updateButtonStates();
            this.showProgress();
            
            const config = {
                baseUrl: this.baseUrlInput.value.trim(),
                maxConcurrent: parseInt(this.maxConcurrentInput.value),
                outputDir: this.outputDirInput.value.trim()
            };
            
            this.addLog('info', `Scraping başlatılıyor: ${config.baseUrl}`);
            this.addLog('info', `Eşzamanlı istek sayısı: ${config.maxConcurrent}`);
            this.addLog('info', `Çıktı klasörü: ${config.outputDir}`);
            
            // Simüle edilmiş progress (gerçek implementasyon için backend API gerekli)
            await this.simulateScraping(config);
            
            this.addLog('success', 'Scraping işlemi başarıyla tamamlandı!');
            this.convertToJsonBtn.disabled = false;
            this.fileTreeCard.style.display = 'block';
            this.updateFileTree();
            
        } catch (error) {
            this.addLog('error', `Scraping hatası: ${error.message}`);
        } finally {
            this.isRunning = false;
            this.updateButtonStates();
            this.hideProgress();
        }
    }

    async simulateScraping(config) {
        // Bu fonksiyon gerçek implementasyonda backend API çağrısı yapacak
        const totalSteps = 100;
        let currentStep = 0;
        
        for (let i = 0; i < totalSteps; i++) {
            if (!this.isRunning) break;
            
            await new Promise(resolve => setTimeout(resolve, 200));
            
            currentStep++;
            const percentage = (currentStep / totalSteps) * 100;
            
            // Simüle edilmiş stats güncelleme
            if (Math.random() > 0.1) {
                this.stats.downloaded++;
            } else {
                this.stats.failed++;
            }
            
            this.stats.queue = Math.max(0, Math.floor(Math.random() * 50));
            
            this.updateProgress(percentage, `İndiriliyor... (${currentStep}/${totalSteps})`);
            this.updateStats();
            
            // Ara log mesajları
            if (currentStep % 10 === 0) {
                this.addLog('info', `${currentStep} dosya işlendi`);
            }
        }
        
        this.updateProgress(100, 'Scraping tamamlandı!');
    }

    async convertToJson() {
        if (this.isRunning) return;
        
        try {
            this.isRunning = true;
            this.updateButtonStates();
            this.showProgress();
            
            this.addLog('info', 'HTML dosyaları JSON formatına dönüştürülüyor...');
            
            // Simüle edilmiş dönüştürme
            await this.simulateJsonConversion();
            
            this.addLog('success', 'JSON dönüştürme işlemi tamamlandı!');
            
        } catch (error) {
            this.addLog('error', `JSON dönüştürme hatası: ${error.message}`);
        } finally {
            this.isRunning = false;
            this.updateButtonStates();
            this.hideProgress();
        }
    }

    async simulateJsonConversion() {
        const totalSteps = 50;
        let currentStep = 0;
        
        for (let i = 0; i < totalSteps; i++) {
            if (!this.isRunning) break;
            
            await new Promise(resolve => setTimeout(resolve, 150));
            
            currentStep++;
            const percentage = (currentStep / totalSteps) * 100;
            
            this.updateProgress(percentage, `JSON'a dönüştürülüyor... (${currentStep}/${totalSteps})`);
            
            if (currentStep % 10 === 0) {
                this.addLog('info', `${currentStep} dosya JSON'a dönüştürüldü`);
            }
        }
        
        this.updateProgress(100, 'JSON dönüştürme tamamlandı!');
    }

    stopProcess() {
        this.isRunning = false;
        this.updateButtonStates();
        this.hideProgress();
        this.addLog('warning', 'İşlem kullanıcı tarafından durduruldu.');
    }

    updateButtonStates() {
        this.startScrapingBtn.disabled = this.isRunning || !this.validateForm();
        this.convertToJsonBtn.disabled = this.isRunning || !this.convertToJsonBtn.disabled;
        this.stopProcessBtn.disabled = !this.isRunning;
        
        // Button text güncelleme
        if (this.isRunning) {
            this.startScrapingBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Çalışıyor...';
            this.convertToJsonBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Dönüştürülüyor...';
        } else {
            this.startScrapingBtn.innerHTML = '<i class="fas fa-download me-2"></i>Scraping Başlat';
            this.convertToJsonBtn.innerHTML = '<i class="fas fa-file-code me-2"></i>JSON\'a Dönüştür';
        }
    }

    updateFileTree() {
        // Simüle edilmiş dosya ağacı
        const mockFiles = [
            'index.html',
            'pages/page1.html',
            'pages/page2.html',
            'pages/subpages/subpage1.html',
            'pages/subpages/subpage2.html',
            'content/article1.html',
            'content/article2.html',
            'assets/images/logo.png',
            'assets/css/style.css',
            'assets/js/script.js'
        ];
        
        let treeHTML = '';
        
        mockFiles.forEach(file => {
            const isDirectory = file.includes('/');
            const fileName = file.split('/').pop();
            const icon = isDirectory ? 'folder' : 'file';
            const type = fileName.split('.').pop();
            
            treeHTML += `
                <div class="tree-item">
                    <i class="fas fa-${icon} tree-icon"></i>
                    <span class="status-indicator status-ready"></span>
                    <span class="file-name">${fileName}</span>
                    <small class="text-muted ms-auto">${type.toUpperCase()}</small>
                </div>
            `;
        });
        
        this.fileTree.innerHTML = treeHTML;
    }

    // Utility methods
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}:${(minutes % 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`;
        }
    }
}

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    window.noterlikApp = new NoterlikApp();
});

// Sayfa kapatılırken temizlik
window.addEventListener('beforeunload', () => {
    if (window.noterlikApp && window.noterlikApp.isRunning) {
        window.noterlikApp.stopProcess();
    }
});
