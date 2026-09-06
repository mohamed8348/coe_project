import copy
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ERPEvent:
    event_id: str
    event_type: str  # e.g. 'INVOICE_SUBMITTED', 'PAYMENT_APPROVED'
    entity_id: str   # e.g. invoice ID
    payload: dict
    timestamp: datetime
    sequence_number: int

class ChaosEngine:
    """Simulates chaos in ERP event streams."""
    
    # --- Chaos Injectors ---
    
    def inject_delayed_event(self, event: ERPEvent, delay_minutes: int = 15) -> ERPEvent:
        """Clones event with delayed timestamp."""
        delayed = copy.deepcopy(event)
        delayed.timestamp += timedelta(minutes=delay_minutes)
        return delayed
        
    def inject_duplicate_event(self, event: ERPEvent) -> List[ERPEvent]:
        """Returns original + duplicate with same event_id."""
        return [event, copy.deepcopy(event)]
        
    def inject_out_of_order_event(self, events: List[ERPEvent]) -> List[ERPEvent]:
        """Shuffles events so their physical order differs from sequence_number order."""
        shuffled = list(events)
        random.shuffle(shuffled)
        return shuffled

    # --- Anomaly Detection ---
    
    def detect_delayed_approval(self, events: List[ERPEvent], threshold_minutes: int = 10) -> List[dict]:
        """Finds approvals that arrived too late relative to submissions."""
        anomalies = []
        submissions = {e.entity_id: e for e in events if e.event_type == 'INVOICE_SUBMITTED'}
        
        for e in events:
            if e.event_type == 'PAYMENT_APPROVED' and e.entity_id in submissions:
                sub_event = submissions[e.entity_id]
                delay = (e.timestamp - sub_event.timestamp).total_seconds() / 60.0
                if delay > threshold_minutes:
                    anomalies.append({
                        'event_id': e.event_id,
                        'entity_id': e.entity_id,
                        'delay_minutes': delay,
                        'threshold': threshold_minutes
                    })
        return anomalies

    def detect_duplicate_events(self, events: List[ERPEvent]) -> List[dict]:
        """Finds events with same event_id."""
        anomalies = []
        seen = set()
        for e in events:
            if e.event_id in seen:
                anomalies.append({
                    'event_id': e.event_id,
                    'type': 'duplicate_event_id'
                })
            seen.add(e.event_id)
        return anomalies

    def detect_out_of_order(self, events: List[ERPEvent]) -> List[dict]:
        """Finds events where sequence_number order != physical array order."""
        anomalies = []
        for i in range(1, len(events)):
            if events[i].sequence_number < events[i-1].sequence_number:
                anomalies.append({
                    'index': i,
                    'event_id': events[i].event_id,
                    'sequence_number': events[i].sequence_number,
                    'previous_sequence': events[i-1].sequence_number,
                    'type': 'out_of_order'
                })
        return anomalies

    # --- State Reconciler ---
    
    def reconcile_state(self, events: List[ERPEvent]) -> dict:
        """
        Given a chaotic event stream, produce a consistent final state.
        Uses idempotency key (event_id) to deduplicate.
        Re-sorts by sequence_number.
        """
        anomalies_detected = []
        
        # Detect Anomalies Before Reconciling
        dups = self.detect_duplicate_events(events)
        if dups:
            anomalies_detected.extend(dups)
            
        ooo = self.detect_out_of_order(events)
        if ooo:
            anomalies_detected.extend(ooo)
            
        # Deduplicate
        unique_events = {}
        for e in events:
            if e.event_id not in unique_events:
                unique_events[e.event_id] = e
        
        # Sort by sequence
        sorted_events = sorted(unique_events.values(), key=lambda x: x.sequence_number)
        
        # Apply to state
        state = {}
        consistency = True
        
        for e in sorted_events:
            entity = state.setdefault(e.entity_id, {'status': 'UNKNOWN', 'history': []})
            entity['history'].append(e.event_type)
            
            # Simple Business Rules
            if e.event_type == 'INVOICE_SUBMITTED':
                entity['status'] = 'PENDING_APPROVAL'
            elif e.event_type == 'PAYMENT_APPROVED':
                if entity['status'] != 'PENDING_APPROVAL':
                    consistency = False
                entity['status'] = 'APPROVED'
                
        return {
            'final_state': state,
            'events_processed': len(sorted_events),
            'anomalies_detected': anomalies_detected,
            'consistency_maintained': consistency
        }

    # --- Demo Runner ---
    
    def run_chaos_scenario(self, scenario_name: str) -> dict:
        print(f"\\n--- Running Scenario: {scenario_name} ---")
        base_time = datetime.now()
        
        e1 = ERPEvent("evt_1", "INVOICE_SUBMITTED", "inv_123", {"amount": 500}, base_time, 1)
        e2 = ERPEvent("evt_2", "PAYMENT_APPROVED", "inv_123", {"approver": "boss"}, base_time + timedelta(minutes=5), 2)
        
        events = [e1, e2]
        
        if scenario_name == 'delayed_approval':
            events[1] = self.inject_delayed_event(events[1], delay_minutes=20)
            delayed_anoms = self.detect_delayed_approval(events, threshold_minutes=10)
            print(f"Delayed Approvals Detected: {delayed_anoms}")
            
        elif scenario_name == 'duplicate_invoice':
            events = self.inject_duplicate_event(events[0]) + [events[1]]
            
        elif scenario_name == 'out_of_order_payment':
            events = self.inject_out_of_order_event(events)
            
        result = self.reconcile_state(events)
        print("Reconciliation Result:")
        import json
        print(json.dumps(result, indent=2, default=str))
        return result

def main():
    engine = ChaosEngine()
    engine.run_chaos_scenario('delayed_approval')
    engine.run_chaos_scenario('duplicate_invoice')
    engine.run_chaos_scenario('out_of_order_payment')

if __name__ == '__main__':
    main()
