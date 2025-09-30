<template>
  <div class="slider-captcha">
    <div class="captcha-track" :class="{ success: isSuccess, error: isError }">
      <div class="captcha-slider" :style="{ left: sliderLeft + 'px' }" @mousedown="handleMouseDown" @touchstart="handleTouchStart">
        <span v-if="!isSuccess">→</span>
        <span v-else>✓</span>
      </div>
      <div class="captcha-text" v-if="!isSuccess && !isError">
        {{ sliderLeft === 0 ? '向右滑动验证' : '继续滑动' }}
      </div>
      <div class="captcha-text success-text" v-if="isSuccess">
        验证成功
      </div>
      <div class="captcha-text error-text" v-if="isError">
        验证失败，请重试
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SliderCaptcha',
  emits: ['success'],
  data() {
    return {
      startX: 0,
      sliderLeft: 0,
      isDragging: false,
      isSuccess: false,
      isError: false,
      trackWidth: 0
    }
  },
  mounted() {
    this.trackWidth = this.$el.querySelector('.captcha-track').offsetWidth
  },
  methods: {
    handleMouseDown(e) {
      if (this.isSuccess) return
      this.isDragging = true
      this.startX = e.clientX
      this.isError = false
      
      document.addEventListener('mousemove', this.handleMouseMove)
      document.addEventListener('mouseup', this.handleMouseUp)
    },
    handleTouchStart(e) {
      if (this.isSuccess) return
      this.isDragging = true
      this.startX = e.touches[0].clientX
      this.isError = false
      
      document.addEventListener('touchmove', this.handleTouchMove)
      document.addEventListener('touchend', this.handleTouchEnd)
    },
    handleMouseMove(e) {
      if (!this.isDragging) return
      
      const moveX = e.clientX - this.startX
      const maxMove = this.trackWidth - 50 // 50 是滑块宽度
      
      if (moveX > 0 && moveX <= maxMove) {
        this.sliderLeft = moveX
      }
    },
    handleTouchMove(e) {
      if (!this.isDragging) return
      
      const moveX = e.touches[0].clientX - this.startX
      const maxMove = this.trackWidth - 50
      
      if (moveX > 0 && moveX <= maxMove) {
        this.sliderLeft = moveX
      }
    },
    handleMouseUp() {
      if (!this.isDragging) return
      this.isDragging = false
      
      document.removeEventListener('mousemove', this.handleMouseMove)
      document.removeEventListener('mouseup', this.handleMouseUp)
      
      this.checkSuccess()
    },
    handleTouchEnd() {
      if (!this.isDragging) return
      this.isDragging = false
      
      document.removeEventListener('touchmove', this.handleTouchMove)
      document.removeEventListener('touchend', this.handleTouchEnd)
      
      this.checkSuccess()
    },
    checkSuccess() {
      const maxMove = this.trackWidth - 50
      const threshold = maxMove * 0.9 // 滑动到90%即可
      
      if (this.sliderLeft >= threshold) {
        this.isSuccess = true
        this.sliderLeft = maxMove
        this.$emit('success')
      } else {
        this.isError = true
        setTimeout(() => {
          this.reset()
        }, 1000)
      }
    },
    reset() {
      this.sliderLeft = 0
      this.isSuccess = false
      this.isError = false
      this.isDragging = false
    }
  }
}
</script>

<style scoped>
.slider-captcha {
  margin: 20px 0;
}

.captcha-track {
  position: relative;
  width: 100%;
  height: 40px;
  background: #f0f2f5;
  border-radius: 4px;
  transition: all 0.3s;
  overflow: hidden;
}

.captcha-track.success {
  background: linear-gradient(to right, #52c41a, #95de64);
}

.captcha-track.error {
  background: linear-gradient(to right, #ff4d4f, #ff7875);
}

.captcha-slider {
  position: absolute;
  left: 0;
  top: 0;
  width: 50px;
  height: 40px;
  background: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: background 0.3s;
  user-select: none;
  z-index: 2;
}

.captcha-slider:active {
  cursor: grabbing;
}

.captcha-slider span {
  font-size: 18px;
  font-weight: bold;
  color: #1677ff;
}

.captcha-track.success .captcha-slider {
  background: #52c41a;
}

.captcha-track.success .captcha-slider span {
  color: white;
}

.captcha-track.error .captcha-slider {
  background: #ff4d4f;
}

.captcha-track.error .captcha-slider span {
  color: white;
}

.captcha-text {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8c8c8c;
  font-size: 14px;
  pointer-events: none;
  z-index: 1;
}

.success-text {
  color: white;
  font-weight: 500;
}

.error-text {
  color: white;
  font-weight: 500;
}
</style>
