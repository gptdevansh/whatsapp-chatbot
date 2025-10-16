// Dashboard Page JS - Fetches stats and renders overview

document.addEventListener('DOMContentLoaded', async function() {
  // Auth check
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
    return;
  }

  const totalUsersEl = document.getElementById('totalUsers');
  const totalChatsEl = document.getElementById('totalChats');
  const latestMessageEl = document.getElementById('latestMessage');

  // Fetch stats from your backend
  try {
    const res = await fetch('/api/v1/admin/stats', {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
    });
    
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
        return;
      }
      throw new Error('Failed to fetch stats');
    }
    
    const stats = await res.json();
    
    // Animate counter
    const animateCounter = (el, target) => {
      let current = 0;
      const increment = target / 30;
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          el.textContent = target.toLocaleString();
          clearInterval(timer);
        } else {
          el.textContent = Math.floor(current).toLocaleString();
        }
      }, 30);
    };
    
    animateCounter(totalUsersEl, stats.total_users || 0);
    animateCounter(totalChatsEl, stats.total_messages || 0);
    latestMessageEl.textContent = `${stats.active_users_24h || 0} active in 24h`;
    
    // Create beautiful chart with ApexCharts
    renderActivityChart(stats);
    
  } catch (err) {
    Toastify({
      text: "Error loading dashboard stats",
      duration: 3000,
      gravity: "top",
      position: "right",
      style: {
        background: "linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)",
      }
    }).showToast();
  }
});

function renderActivityChart(stats) {
  // Generate sample data for last 7 days (you can fetch real data from backend)
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const messages = [12, 19, 15, 25, 22, 30, stats.total_messages || 28];
  const users = [3, 5, 4, 7, 6, 9, stats.total_users || 8];
  
  const options = {
    series: [{
      name: 'Messages',
      data: messages
    }, {
      name: 'Users',
      data: users
    }],
    chart: {
      type: 'area',
      height: 350,
      background: 'transparent',
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 2
    },
    colors: ['#25D366', '#7c3aed'],
    fill: {
      type: 'gradient',
      gradient: {
        opacityFrom: 0.6,
        opacityTo: 0.1,
      }
    },
    xaxis: {
      categories: days,
      labels: {
        style: {
          colors: '#9ca3af'
        }
      }
    },
    yaxis: {
      labels: {
        style: {
          colors: '#9ca3af'
        }
      }
    },
    grid: {
      borderColor: '#2a2f4a',
      strokeDashArray: 4
    },
    legend: {
      position: 'top',
      labels: {
        colors: '#9ca3af'
      }
    },
    tooltip: {
      theme: 'dark',
      style: {
        fontSize: '12px'
      }
    }
  };

  const chart = new ApexCharts(document.querySelector("#activityChart"), options);
  chart.render();
}
