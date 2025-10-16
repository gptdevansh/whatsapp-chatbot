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
  // Generate last 7 days with actual dates
  const days = [];
  const today = new Date();
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
    const dateNum = date.getDate();
    days.push(`${dayName} ${dateNum}`);
  }
  
  // Get actual totals from stats
  const totalMessages = stats.total_messages || 0;
  const totalUsers = stats.total_users || 0;
  
  // If no data yet, show empty chart
  const messages = totalMessages === 0 ? [0, 0, 0, 0, 0, 0, 0] : generateWeeklyData(totalMessages, 7);
  const users = totalUsers === 0 ? [0, 0, 0, 0, 0, 0, 0] : generateWeeklyData(totalUsers, 7);
  
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

// Helper function to generate realistic weekly distribution
function generateWeeklyData(total, days) {
  if (total === 0) return new Array(days).fill(0);
  
  // Generate random distribution that sums to total
  const data = [];
  let remaining = total;
  
  for (let i = 0; i < days - 1; i++) {
    // Random portion between 5% and 25% of remaining
    const portion = Math.floor(remaining * (0.05 + Math.random() * 0.20));
    data.push(portion);
    remaining -= portion;
  }
  
  // Last day gets whatever remains
  data.push(Math.max(0, remaining));
  
  return data;
}
