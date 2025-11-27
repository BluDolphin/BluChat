from nicegui import ui


columns = [
    {'name': 'active', 'label': 'active', 'field': 'active'},
    {'name': 'number', 'label': 'number', 'field': 'number'},
    {'name': 'action', 'label': 'Action', 'field': 'action'},
]
rows = [
    {'active': 'y', 'number': 'test1'},
    {'active': 'n', 'number': 'test2'},
    {'active': 'y', 'number': 'test3'}
]
table = ui.table(columns=columns, rows=rows)

def action(row):
    number = row['number']
    ui.notify(f'Action for {number}')

table.add_slot('body-cell-action', '''
    <q-td :props="props">
        <q-btn label="Action" @click="$parent.$emit('click_action', props.row)" flat />
    </q-td>
''')

table.on('click_action', lambda e: action(e.args))

ui.run()
