"""
🧪 PHARMACEUTICAL & RESEARCH API TEST SUITE
Stellar Logic AI - Pharmaceutical Security & Research Integrity API Testing

Comprehensive testing for clinical trial security, drug development protection,
research integrity, and pharmaceutical industry compliance endpoints.
"""

import requests
import json
import time
import logging
from datetime import datetime
import random
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PharmaceuticalResearchAPITestSuite:
    """Test suite for Pharmaceutical & Research Security API"""
    
    def __init__(self, base_url="http://localhost:5009"):
        self.base_url = base_url
        self.test_results = []
        self.performance_metrics = []
        
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("Starting Pharmaceutical & Research API Test Suite")
        print("🧪 Pharmaceutical & Research API Test Suite")
        print("=" * 60)
        
        # Test endpoints
        self.test_health_check()
        self.test_pharma_analysis()
        self.test_dashboard_data()
        self.test_alerts_endpoint()
        self.test_data_manipulation()
        self.test_researchers_endpoint()
        self.test_institutions_endpoint()
        self.test_clinical_trials_endpoint()
        self.test_drugs_endpoint()
        self.test_regulatory_compliance()
        self.test_supply_chain()
        self.test_statistics_endpoint()
        
        # Generate summary
        self.generate_test_summary()
        
    def test_health_check(self):
        """Test health check endpoint"""
        logger.info("Testing health check endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.test_results.append({
                    'test': 'Health Check',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {data.get('status')}, AI Core: {data.get('ai_core_status', {}).get('ai_core_connected')}"
                })
                print(f"✅ Health Check: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Health Check',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Health Check: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Health Check',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Health Check: ERROR ({str(e)})")
    
    def test_pharma_analysis(self):
        """Test pharmaceutical analysis endpoint"""
        logger.info("Testing pharmaceutical analysis endpoint")
        
        test_events = [
            {
                'event_id': 'PHARMA_001',
                'researcher_id': 'RESEARCHER_001',
                'institution_id': 'INST_001',
                'trial_id': 'TRIAL_001',
                'drug_id': 'DRUG_001',
                'research_phase': 'phase_iii',
                'institution_type': 'pharmaceutical_company',
                'drug_type': 'small_molecule',
                'researcher_name': 'Dr. John Smith',
                'specialization': 'Oncology',
                'experience_years': 15,
                'publications_count': 45,
                'clinical_trials_count': 12,
                'regulatory_violations': 0,
                'security_clearance': 'enhanced',
                'trial_phase': 'phase_iii',
                'participant_count': 2500,
                'duration_months': 24,
                'trial_type': 'interventional',
                'primary_endpoints': ['overall_survival', 'progression_free_survival'],
                'secondary_endpoints': ['response_rate', 'safety_profile'],
                'blinding_method': 'double_blind',
                'control_group': True,
                'drug_name': 'Oncotinib',
                'mechanism_of_action': 'Tyrosine kinase inhibitor',
                'indication': 'Non-small cell lung cancer',
                'dosage_form': 'tablet',
                'administration_route': 'oral',
                'patent_status': 'patented',
                'regulatory_status': 'approved',
                'clinical_data': {
                    'efficacy_rate': 0.65,
                    'response_rate': 0.58,
                    'median_survival': 14.2,
                    'adverse_events': 150
                },
                'laboratory_results': {
                    'bioavailability': 0.85,
                    'half_life': 12.5,
                    'protein_binding': 0.95,
                    'metabolism': 'hepatic'
                },
                'statistical_analysis': {
                    'p_value': 0.001,
                    'confidence_interval': '95%',
                    'hazard_ratio': 0.68,
                    'sample_size': 2500
                },
                'adverse_events': [
                    {'type': 'nausea', 'severity': 'mild', 'frequency': 'common'},
                    {'type': 'fatigue', 'severity': 'moderate', 'frequency': 'common'},
                    {'type': 'diarrhea', 'severity': 'mild', 'frequency': 'occasional'}
                ],
                'efficacy_metrics': {
                    'objective_response_rate': 0.58,
                    'disease_control_rate': 0.72,
                    'time_to_progression': 8.5,
                    'overall_survival': 18.2
                },
                'safety_profile': {
                    'grade_3_adverse_events': 0.15,
                    'treatment_discontinuation': 0.08,
                    'serious_adverse_events': 25,
                    'deaths_related': 2
                },
                'fda_regulations': {
                    'ind_submission': True,
                    'nda_approval': True,
                    'post_marketing': True,
                    'adverse_event_reporting': True
                },
                'ema_guidelines': {
                    'ma_submission': True,
                    'conditional_approval': False,
                    'pharmacovigilance': True,
                    'risk_management': True
                },
                'ich_guidelines': {
                    'e6_efficacy': True,
                    'e8_safety': True,
                    'e9_statistics': True,
                    'e10_cmc': True
                },
                'gcp_compliance': 0.95,
                'glp_compliance': 0.92,
                'gmp_compliance': 0.98,
                'data_access_logs': ['2024-01-15 09:00', '2024-01-15 14:30', '2024-01-15 16:45'],
                'system_access_patterns': ['normal', 'normal', 'unusual'],
                'data_modification_history': [],
                'external_collaborations': ['University Lab A', 'Research Institute B'],
                'supply_chain_access': {
                    'raw_materials': 'verified',
                    'manufacturing': 'compliant',
                    'distribution': 'secure'
                },
                'biosecurity_measures': {
                    'biosafety_level': 2,
                    'containment_procedures': True,
                    'personnel_training': True
                },
                'researcher_data': {
                    'age': 45,
                    'gender': 'male',
                    'nationality': 'US',
                    'education': 'MD, PhD'
                },
                'institution_data': {
                    'name': 'PharmaCorp International',
                    'location': 'New York',
                    'type': 'public',
                    'employees': 5000
                },
                'trial_data': {
                    'protocol_version': '3.0',
                    'irb_approval': True,
                    'fda_investigational_new_drug': True,
                    'clinicaltrials_gov_id': 'NCT12345678'
                },
                'drug_data': {
                    'molecular_weight': 450.5,
                    'chemical_formula': 'C23H27FN4O2',
                    'storage_conditions': 'room_temperature',
                    'shelf_life': 24
                }
            },
            {
                'event_id': 'PHARMA_002',
                'researcher_id': 'RESEARCHER_002',
                'institution_id': 'INST_002',
                'trial_id': 'TRIAL_002',
                'drug_id': 'DRUG_002',
                'research_phase': 'phase_ii',
                'institution_type': 'research_institute',
                'drug_type': 'biologic',
                'researcher_name': 'Dr. Sarah Johnson',
                'specialization': 'Immunology',
                'experience_years': 12,
                'publications_count': 38,
                'clinical_trials_count': 8,
                'regulatory_violations': 0,
                'security_clearance': 'top_secret',
                'trial_phase': 'phase_ii',
                'participant_count': 450,
                'duration_months': 18,
                'trial_type': 'observational',
                'primary_endpoints': ['immune_response', 'safety'],
                'secondary_endpoints': ['biomarker_analysis', 'quality_of_life'],
                'blinding_method': 'open_label',
                'control_group': False,
                'drug_name': 'ImmunoTherapy-X',
                'mechanism_of_action': 'PD-1 inhibitor',
                'indication': 'Advanced melanoma',
                'dosage_form': 'injection',
                'administration_route': 'intravenous',
                'patent_status': 'patent_pending',
                'regulatory_status': 'investigational',
                'clinical_data': {
                    'immune_response_rate': 0.72,
                    'objective_response_rate': 0.28,
                    'median_duration': 11.8,
                    'adverse_events': 85
                },
                'laboratory_results': {
                    'bioavailability': 0.95,
                    'half_life': 25.3,
                    'protein_binding': 0.99,
                    'metabolism': 'proteolytic'
                },
                'statistical_analysis': {
                    'p_value': 0.003,
                    'confidence_interval': '90%',
                    'hazard_ratio': 0.55,
                    'sample_size': 450
                },
                'adverse_events': [
                    {'type': 'immune_related', 'severity': 'moderate', 'frequency': 'common'},
                    {'type': 'infusion_reaction', 'severity': 'mild', 'frequency': 'occasional'},
                    {'type': 'fatigue', 'severity': 'moderate', 'frequency': 'common'}
                ],
                'efficacy_metrics': {
                    'immune_response_rate': 0.72,
                    'disease_control_rate': 0.65,
                    'time_to_response': 2.3,
                    'duration_of_response': 8.7
                },
                'safety_profile': {
                    'grade_3_adverse_events': 0.12,
                    'treatment_discontinuation': 0.05,
                    'serious_adverse_events': 18,
                    'deaths_related': 1
                },
                'fda_regulations': {
                    'ind_submission': True,
                    'nda_approval': False,
                    'post_marketing': False,
                    'adverse_event_reporting': True
                },
                'ema_guidelines': {
                    'ma_submission': True,
                    'conditional_approval': True,
                    'pharmacovigilance': True,
                    'risk_management': True
                },
                'ich_guidelines': {
                    'e6_efficacy': True,
                    'e8_safety': True,
                    'e9_statistics': True,
                    'e10_cmc': True
                },
                'gcp_compliance': 0.98,
                'glp_compliance': 0.95,
                'gmp_compliance': 0.97,
                'data_access_logs': ['2024-01-15 08:00', '2024-01-15 13:00', '2024-01-15 17:00'],
                'system_access_patterns': ['normal', 'normal', 'normal'],
                'data_modification_history': [],
                'external_collaborations': ['Hospital C', 'University D'],
                'supply_chain_access': {
                    'raw_materials': 'verified',
                    'manufacturing': 'compliant',
                    'distribution': 'secure'
                },
                'biosecurity_measures': {
                    'biosafety_level': 3,
                    'containment_procedures': True,
                    'personnel_training': True
                },
                'researcher_data': {
                    'age': 38,
                    'gender': 'female',
                    'nationality': 'Canada',
                    'education': 'MD, PhD'
                },
                'institution_data': {
                    'name': 'Advanced Research Institute',
                    'location': 'Boston',
                    'type': 'nonprofit',
                    'employees': 800
                },
                'trial_data': {
                    'protocol_version': '2.0',
                    'irb_approval': True,
                    'fda_investigational_new_drug': True,
                    'clinicaltrials_gov_id': 'NCT87654321'
                },
                'drug_data': {
                    'molecular_weight': 150000,
                    'protein_sequence': 'monoclonal_antibody',
                    'storage_conditions': 'refrigerated',
                    'shelf_life': 36
                }
            }
        ]
        
        for i, event in enumerate(test_events):
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}/api/pharma/analyze", json=event)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results.append({
                        'test': f'Pharma Analysis {i+1}',
                        'status': 'PASS',
                        'response_time': response_time,
                        'details': f"Status: {data.get('status')}, Security Level: {data.get('alert', {}).get('security_level', 'N/A')}"
                    })
                    print(f"✅ Pharma Analysis {i+1}: PASS ({response_time:.2f}ms)")
                else:
                    self.test_results.append({
                        'test': f'Pharma Analysis {i+1}',
                        'status': 'FAIL',
                        'response_time': response_time,
                        'details': f"Status Code: {response.status_code}"
                    })
                    print(f"❌ Pharma Analysis {i+1}: FAIL ({response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    'test': f'Pharma Analysis {i+1}',
                    'status': 'ERROR',
                    'response_time': 0,
                    'details': str(e)
                })
                print(f"❌ Pharma Analysis {i+1}: ERROR ({str(e)})")
    
    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        logger.info("Testing dashboard data endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/dashboard")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Researchers: {metrics.get('researchers_monitored')}, Security Score: {metrics.get('security_score')}%"
                })
                print(f"✅ Dashboard Data: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Dashboard Data',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Dashboard Data: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Dashboard Data',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Dashboard Data: ERROR ({str(e)})")
    
    def test_alerts_endpoint(self):
        """Test alerts endpoint"""
        logger.info("Testing alerts endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/alerts?limit=10")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                alerts = data.get('alerts', [])
                self.test_results.append({
                    'test': 'Alerts Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Alerts Count: {len(alerts)}, Total: {data.get('total_count')}"
                })
                print(f"✅ Alerts Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Alerts Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Alerts Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Alerts Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Alerts Endpoint: ERROR ({str(e)})")
    
    def test_data_manipulation(self):
        """Test data manipulation endpoint"""
        logger.info("Testing data manipulation endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/data-manipulation")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_manipulation_status')
                accuracy = data.get('detection_accuracy')
                self.test_results.append({
                    'test': 'Data Manipulation',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Accuracy: {accuracy}"
                })
                print(f"✅ Data Manipulation: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Data Manipulation',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Data Manipulation: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Data Manipulation',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Data Manipulation: ERROR ({str(e)})")
    
    def test_researchers_endpoint(self):
        """Test researchers endpoint"""
        logger.info("Testing researchers endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/researchers")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                researchers = data.get('researchers', [])
                self.test_results.append({
                    'test': 'Researchers Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Researchers: {len(researchers)}, Active: {data.get('active_researchers')}"
                })
                print(f"✅ Researchers Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Researchers Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Researchers Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Researchers Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Researchers Endpoint: ERROR ({str(e)})")
    
    def test_institutions_endpoint(self):
        """Test institutions endpoint"""
        logger.info("Testing institutions endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/institutions")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                institutions = data.get('institutions', [])
                self.test_results.append({
                    'test': 'Institutions Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Institutions: {len(institutions)}, Active: {data.get('active_institutions')}"
                })
                print(f"✅ Institutions Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Institutions Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Institutions Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Institutions Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Institutions Endpoint: ERROR ({str(e)})")
    
    def test_clinical_trials_endpoint(self):
        """Test clinical trials endpoint"""
        logger.info("Testing clinical trials endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/clinical-trials")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                trials = data.get('trials', [])
                self.test_results.append({
                    'test': 'Clinical Trials Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Trials: {len(trials)}, Active: {data.get('active_trials')}"
                })
                print(f"✅ Clinical Trials Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Clinical Trials Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Clinical Trials Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Clinical Trials Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Clinical Trials Endpoint: ERROR ({str(e)})")
    
    def test_drugs_endpoint(self):
        """Test drugs endpoint"""
        logger.info("Testing drugs endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/drugs")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                drugs = data.get('drugs', [])
                self.test_results.append({
                    'test': 'Drugs Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Drugs: {len(drugs)}, Active: {data.get('active_drugs')}"
                })
                print(f"✅ Drugs Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Drugs Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Drugs Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Drugs Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Drugs Endpoint: ERROR ({str(e)})")
    
    def test_regulatory_compliance(self):
        """Test regulatory compliance endpoint"""
        logger.info("Testing regulatory compliance endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/regulatory-compliance")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_compliance_status')
                metrics = data.get('compliance_metrics', {})
                self.test_results.append({
                    'test': 'Regulatory Compliance',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, FDA Adherence: {metrics.get('fda_regulation_adherence')}"
                })
                print(f"✅ Regulatory Compliance: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Regulatory Compliance',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Regulatory Compliance: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Regulatory Compliance',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Regulatory Compliance: ERROR ({str(e)})")
    
    def test_supply_chain(self):
        """Test supply chain endpoint"""
        logger.info("Testing supply chain endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/supply-chain")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('overall_supply_chain_status')
                metrics = data.get('supply_chain_metrics', {})
                self.test_results.append({
                    'test': 'Supply Chain',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Status: {status}, Raw Material Sourcing: {metrics.get('raw_material_sourcing')}"
                })
                print(f"✅ Supply Chain: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Supply Chain',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Supply Chain: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Supply Chain',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Supply Chain: ERROR ({str(e)})")
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        logger.info("Testing statistics endpoint")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/pharma/stats")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                overview = data.get('overview', {})
                performance = data.get('performance', {})
                self.test_results.append({
                    'test': 'Statistics Endpoint',
                    'status': 'PASS',
                    'response_time': response_time,
                    'details': f"Researchers: {overview.get('researchers_monitored')}, Response Time: {performance.get('average_response_time')}ms"
                })
                print(f"✅ Statistics Endpoint: PASS ({response_time:.2f}ms)")
            else:
                self.test_results.append({
                    'test': 'Statistics Endpoint',
                    'status': 'FAIL',
                    'response_time': response_time,
                    'details': f"Status Code: {response.status_code}"
                })
                print(f"❌ Statistics Endpoint: FAIL ({response.status_code})")
                
        except Exception as e:
            self.test_results.append({
                'test': 'Statistics Endpoint',
                'status': 'ERROR',
                'response_time': 0,
                'details': str(e)
            })
            print(f"❌ Statistics Endpoint: ERROR ({str(e)})")
    
    def generate_test_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")
        print(f"Average Response Time: {avg_response_time:.2f}ms")
        print(f"Min Response Time: {min_response_time:.2f}ms")
        print(f"Max Response Time: {max_response_time:.2f}ms")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "💥"
            print(f"{status_icon} {result['test']}: {result['status']} ({result['response_time']:.2f}ms)")
            print(f"   Details: {result['details']}")
        
        print("\n🎯 PERFORMANCE ANALYSIS:")
        if avg_response_time < 100:
            print("✅ EXCELLENT - Average response time under 100ms")
        elif avg_response_time < 200:
            print("✅ GOOD - Average response time under 200ms")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Average response time above 200ms")
        
        if passed_tests / total_tests >= 0.95:
            print("✅ EXCELLENT - Success rate above 95%")
        elif passed_tests / total_tests >= 0.85:
            print("✅ GOOD - Success rate above 85%")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Success rate below 85%")
        
        print("\n🏥 Pharmaceutical & Research API Test Complete!")

if __name__ == "__main__":
    # Run the test suite
    test_suite = PharmaceuticalResearchAPITestSuite()
    test_suite.run_all_tests()
