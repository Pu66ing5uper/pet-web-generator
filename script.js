// ==================== 全局变量 ====================
let currentState = 'idle'; // 状态机: 'idle' 待机, 'playing' 播放中
let petData = null; // 将用来存放从C同学那里获取的数据

// ==================== 页面主要元素 ====================
const videoPlayer = document.getElementById('pet-video');
const petNameElement = document.getElementById('pet-name');
const buttonsContainer = document.getElementById('interaction-buttons');
const statusHint = document.getElementById('status-hint');

// ==================== 主函数：初始化一切 ====================
async function init() {
    console.log('正在初始化宠物网页...');
    statusHint.textContent = '正在加载宠物数据...';

    // TODO: 这里是你要修改的重点！
    // 方法1：直接使用C同学提供的JSON对象（将下面petDataConfig替换成真实的）
    // petData = getDataFromVariable();

    // 方法2：从C同学提供的URL获取JSON（推荐！）
    const jsonUrl = 'https://raw.githubusercontent.com/Pu66ing5uper/pet-web-generator/refs/heads/main/deploy_output/final_pet_data.json'; // 请替换为真实URL
    petData = await fetchDataFromUrl(jsonUrl);

    if (!petData) {
        statusHint.textContent = '加载失败，请检查数据。';
        return;
    }

    // 更新页面信息
    petNameElement.textContent = `你好，我是${petData.petName}！`;
    videoPlayer.src = petData.idleAnimation; // 设置待机动画
    videoPlayer.loop = true; // 待机动画循环播放

    // 创建互动按钮
    createInteractionButtons();

    statusHint.textContent = `${petData.petName}正在待机，可以互动了！`;
    console.log('初始化完成。');
}

// 示例：从URL获取数据（你需要让C同学提供这个URL）
async function fetchDataFromUrl(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log('从网络加载数据成功:', data);
        return data;
    } catch (error) {
        console.error('加载数据失败:', error);
        statusHint.textContent = '加载数据失败，请检查网络或URL。';
        return null;
    }
}

// 示例：直接使用数据（调试用）
function getDataFromVariable() {
    // 这是模拟数据，用于测试。实际开发时请替换。
    return {
        "petName": "测试小白",
        "idleAnimation": "https://your-bucket.cos.ap-region.myqcloud.com/pets/idle.mp4",
        "interactions": [
            {
                "action": "摸头",
                "animation": "https://your-bucket.cos.ap-region.myqcloud.com/pets/feedback.mp4",
                "triggerButtonText": "摸摸头"
            }
        ]
    };
}

// ==================== 核心功能：创建按钮和状态机 ====================
function createInteractionButtons() {
    // 清空现有按钮
    buttonsContainer.querySelectorAll('button').forEach(btn => btn.remove());

    petData.interactions.forEach(interaction => {
        const button = document.createElement('button');
        button.textContent = interaction.triggerButtonText;
        button.style.backgroundColor = '#2196F3'; // 蓝色按钮

        // 按钮点击事件：核心交互逻辑
        button.addEventListener('click', () => {
            if (currentState !== 'idle') {
                console.log('宠物正忙，请稍后...');
                statusHint.textContent = `${petData.petName}正忙呢，等它做完当前动作吧~`;
                return; // 关键：如果不在待机状态，则忽略点击
            }

            // 切换到播放状态
            enterPlayingState();
            statusHint.textContent = `${petData.petName}正在【${interaction.action}】...`;

            // 切换到反馈动画
            videoPlayer.src = interaction.animation;
            videoPlayer.loop = false; // 反馈动画不循环

            // 监听动画播放结束
            videoPlayer.onended = () => {
                console.log('反馈动画播放完毕，切回待机。');
                exitPlayingState();
                statusHint.textContent = `${petData.petName}回来啦，继续互动吧！`;
            };
        });

        buttonsContainer.appendChild(button);
    });
}

// 进入“播放中”状态：禁用所有按钮
function enterPlayingState() {
    currentState = 'playing';
    document.querySelectorAll('#interaction-buttons button').forEach(btn => {
        btn.disabled = true;
    });
}

// 退出“播放中”状态：重新启用按钮，切回待机动画
function exitPlayingState() {
    currentState = 'idle';
    videoPlayer.src = petData.idleAnimation;
    videoPlayer.loop = true;
    document.querySelectorAll('#interaction-buttons button').forEach(btn => {
        btn.disabled = false;
    });
}

// ==================== 启动！ ====================
// 当页面加载完毕，开始初始化
window.addEventListener('DOMContentLoaded', init);