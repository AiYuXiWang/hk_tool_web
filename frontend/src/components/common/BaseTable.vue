<template>
  <div class="base-table" :class="{ 'table-loading': loading }">
    <div v-if="title || $slots.header" class="table-header">
      <h3 v-if="title" class="table-title">{{ title }}</h3>
      <div class="table-actions">
        <slot name="header" />
      </div>
    </div>
    
    <div class="table-container" :style="{ height: height }">
      <table class="table" :class="tableClass">
        <thead>
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :class="[
                'table-th',
                column.align ? `text-${column.align}` : '',
                column.sortable ? 'sortable' : '',
                sortBy === column.key ? `sort-${sortOrder}` : ''
              ]"
              :style="{ width: column.width }"
              @click="column.sortable && handleSort(column.key)"
            >
              <span class="th-content">
                {{ column.title }}
                <i 
                  v-if="column.sortable" 
                  class="sort-icon"
                  :class="{
                    'icon-sort-up': sortBy === column.key && sortOrder === 'asc',
                    'icon-sort-down': sortBy === column.key && sortOrder === 'desc',
                    'icon-sort': sortBy !== column.key
                  }"
                ></i>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td :colspan="columns.length" class="loading-cell">
              <div class="loading-content">
                <div class="loading-spinner"></div>
                <span>{{ loadingText }}</span>
              </div>
            </td>
          </tr>
          <tr v-else-if="!data.length" class="empty-row">
            <td :colspan="columns.length" class="empty-cell">
              <div class="empty-content">
                <i class="icon-empty"></i>
                <span>{{ emptyText }}</span>
              </div>
            </td>
          </tr>
          <tr 
            v-else
            v-for="(row, index) in paginatedData" 
            :key="getRowKey(row, index)"
            class="table-row"
            :class="{ 
              'row-selected': selectedRows.includes(getRowKey(row, index)),
              'row-hover': hoverable 
            }"
            @click="handleRowClick(row, index)"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              class="table-td"
              :class="[
                column.align ? `text-${column.align}` : '',
                column.className || ''
              ]"
            >
              <slot 
                v-if="column.slot" 
                :name="column.slot" 
                :row="row" 
                :column="column" 
                :index="index"
              />
              <span v-else-if="column.render">
                {{ column.render(row[column.key], row, index) }}
              </span>
              <span v-else>{{ row[column.key] }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="pagination && data.length > pageSize" class="table-pagination">
      <div class="pagination-info">
        共 {{ data.length }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
      </div>
      <div class="pagination-controls">
        <button 
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
        >
          上一页
        </button>
        <button 
          v-for="page in visiblePages" 
          :key="page"
          class="pagination-btn"
          :class="{ active: page === currentPage }"
          @click="handlePageChange(page)"
        >
          {{ page }}
        </button>
        <button 
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="handlePageChange(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

export interface Column {
  key: string
  title: string
  width?: string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  slot?: string
  render?: (value: any, row: any, index: number) => string
  className?: string
}

interface Props {
  data: any[]
  columns: Column[]
  title?: string
  loading?: boolean
  loadingText?: string
  emptyText?: string
  height?: string
  hoverable?: boolean
  selectable?: boolean
  pagination?: boolean
  pageSize?: number
  rowKey?: string | ((row: any) => string)
  tableClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  columns: () => [],
  loadingText: '加载中...',
  emptyText: '暂无数据',
  hoverable: true,
  selectable: false,
  pagination: false,
  pageSize: 10,
  rowKey: 'id'
})

const emit = defineEmits<{
  rowClick: [row: any, index: number]
  sort: [key: string, order: 'asc' | 'desc']
  selectionChange: [selectedRows: any[]]
}>()

const sortBy = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')
const selectedRows = ref<string[]>([])
const currentPage = ref(1)

const sortedData = computed(() => {
  if (!sortBy.value) return props.data
  
  return [...props.data].sort((a, b) => {
    const aVal = a[sortBy.value]
    const bVal = b[sortBy.value]
    
    if (aVal === bVal) return 0
    
    const result = aVal > bVal ? 1 : -1
    return sortOrder.value === 'asc' ? result : -result
  })
})

const totalPages = computed(() => {
  if (!props.pagination) return 1
  return Math.ceil(props.data.length / props.pageSize)
})

const paginatedData = computed(() => {
  if (!props.pagination) return sortedData.value
  
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return sortedData.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    }
  }
  
  return pages
})

const getRowKey = (row: any, index: number): string => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || index.toString()
}

const handleSort = (key: string) => {
  if (sortBy.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = key
    sortOrder.value = 'asc'
  }
  
  emit('sort', key, sortOrder.value)
}

const handleRowClick = (row: any, index: number) => {
  emit('rowClick', row, index)
  
  if (props.selectable) {
    const key = getRowKey(row, index)
    const selectedIndex = selectedRows.value.indexOf(key)
    
    if (selectedIndex > -1) {
      selectedRows.value.splice(selectedIndex, 1)
    } else {
      selectedRows.value.push(key)
    }
    
    emit('selectionChange', selectedRows.value.map(key => 
      props.data.find((item, idx) => getRowKey(item, idx) === key)
    ).filter(Boolean))
  }
}

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

watch(() => props.data, () => {
  currentPage.value = 1
  selectedRows.value = []
})
</script>

<style scoped>
.base-table {
  background: var(--color-background-primary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-secondary);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-secondary);
  background: var(--color-background-secondary);
}

.table-title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.table-container {
  overflow: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.table-th {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-background-secondary);
  border-bottom: 1px solid var(--color-border-secondary);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-align: left;
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-th.sortable {
  cursor: pointer;
  user-select: none;
}

.table-th.sortable:hover {
  background: var(--color-background-tertiary);
}

.th-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.sort-icon {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.table-td {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border-tertiary);
  color: var(--color-text-primary);
}

.table-row:hover .table-td {
  background: var(--color-background-secondary);
}

.row-selected .table-td {
  background: var(--color-primary-light);
}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.loading-row, .empty-row {
  height: 200px;
}

.loading-cell, .empty-cell {
  text-align: center;
  vertical-align: middle;
  color: var(--color-text-tertiary);
}

.loading-content, .empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-border-secondary);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.table-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-top: 1px solid var(--color-border-secondary);
  background: var(--color-background-secondary);
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pagination-controls {
  display: flex;
  gap: var(--spacing-xs);
}

.pagination-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border-secondary);
  background: var(--color-background-primary);
  color: var(--color-text-primary);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-background-secondary);
  border-color: var(--color-primary);
}

.pagination-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 深色模式 */
@media (prefers-color-scheme: dark) {
  .base-table {
    background: var(--color-background-primary-dark);
    border-color: var(--color-border-secondary-dark);
  }
  
  .table-header {
    background: var(--color-background-secondary-dark);
    border-color: var(--color-border-secondary-dark);
  }
  
  .table-title {
    color: var(--color-text-primary-dark);
  }
  
  .table-th {
    background: var(--color-background-secondary-dark);
    border-color: var(--color-border-secondary-dark);
    color: var(--color-text-secondary-dark);
  }
  
  .table-td {
    border-color: var(--color-border-tertiary-dark);
    color: var(--color-text-primary-dark);
  }
  
  .table-row:hover .table-td {
    background: var(--color-background-tertiary-dark);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: stretch;
  }
  
  .table-pagination {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .pagination-controls {
    justify-content: center;
  }
}
</style>